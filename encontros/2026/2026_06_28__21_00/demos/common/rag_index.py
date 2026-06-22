"""Índice de RAG compartilhado pelas POCs deste encontro (parte 2).

É a fundação reutilizada por retrieval (POC A), rerank (POC B), avaliação (POC C) e
observabilidade (POC D). Mantém o conceito visível: embeddings em memória, BM25 à mão,
fusão por RRF, filtro por tenant FAIL-CLOSED e truncamento de embedding (Matryoshka).

Em produção isto seria um vector DB (HNSW/IVF) + search engine; aqui é pequeno de
propósito, para inspeção.
"""

from __future__ import annotations

import hashlib
import os
from dataclasses import dataclass, field

from .corpus import chunk_corpus, load_corpus
from .textutil import BM25, cosine, minmax, rrf, tokenize
from .tracing import set_output, span


@dataclass
class Candidate:
    chunk_id: str
    doc_id: str
    text: str
    meta: dict
    dense: float = 0.0
    lexical: float = 0.0
    fused: float = 0.0
    rerank: float = 0.0
    embedding: list[float] = field(default_factory=list)


def _truncate(vec: list[float], dims: int | None) -> list[float]:
    """Truncamento estilo Matryoshka: usa só as primeiras `dims` componentes.

    Modelos MRL (ex.: nomic) treinam o vetor para que o prefixo já seja útil, então dá
    para cortar dimensão trocando um pouco de qualidade por menos custo. O cosseno
    normaliza, então não precisamos renormalizar à mão aqui."""
    if dims is None or dims >= len(vec):
        return vec
    return vec[:dims]


class RagIndex:
    def __init__(self, client, corpus_dir: str, *, include_adversarial: bool = False,
                 max_tokens: int = 120, embed_dims: int | None = None) -> None:
        self.client = client
        self.corpus_dir = corpus_dir
        self.max_tokens = max_tokens
        self.embed_dims = embed_dims
        self.docs = load_corpus(corpus_dir, include_adversarial=include_adversarial)
        self.chunks = chunk_corpus(self.docs, max_tokens=max_tokens)
        self.bm25 = BM25().fit([c.tokens for c in self.chunks])
        raw = client.embed([c.text for c in self.chunks])
        self.embeddings = [_truncate(v, embed_dims) for v in raw]

    @property
    def index_version(self) -> str:
        """Identidade do índice = modelo de embedding + chunking + dims + corpus.
        Mudou qualquer um -> índice novo. Vai para a observabilidade (POC D)."""
        embed_model = getattr(self.client, "embed_model", "?")
        dims = self.embed_dims or (len(self.embeddings[0]) if self.embeddings else 0)
        files = ",".join(sorted(os.path.basename(d.path) for d in self.docs))
        raw = f"{embed_model}|maxtok={self.max_tokens}|dims={dims}|{files}"
        h = hashlib.sha1(raw.encode()).hexdigest()[:8]
        return f"{embed_model}@{dims}d-{h}"

    # ---- scores por método ------------------------------------------------ #
    def dense_scores(self, query: str) -> list[float]:
        q = _truncate(self.client.embed([query])[0], self.embed_dims)
        return [cosine(q, e) for e in self.embeddings]

    def lexical_scores(self, query: str) -> list[float]:
        return self.bm25.scores(tokenize(query))

    def retrieve(self, query: str, *, method: str = "hybrid", k: int = 8,
                 tenant: str | None = "mercania") -> list[Candidate]:
        with span(
            f"rag.retrieve:{method}", kind="RETRIEVER",
            inputs={"query": query, "method": method, "k": k, "tenant": tenant},
            attributes={"retrieval.index_version": self.index_version},
        ) as cur:
            dense = self.dense_scores(query)   # gera um span ollama.embed aninhado
            lexical = self.lexical_scores(query)
            order = list(range(len(self.chunks)))
            if method == "dense":
                ranked = sorted(order, key=lambda i: dense[i], reverse=True)
            elif method == "lexical":
                ranked = sorted(order, key=lambda i: lexical[i], reverse=True)
            elif method == "hybrid":
                dr = sorted(order, key=lambda i: dense[i], reverse=True)
                lr = sorted(order, key=lambda i: lexical[i], reverse=True)
                ranked = [doc_id for doc_id, _ in rrf([dr, lr])]
            else:
                raise ValueError(f"método desconhecido: {method}")

            nd, nl = minmax(dense), minmax(lexical)
            # fused score para exibição (RRF normalizado por posição não é trivial; usamos
            # média dos scores normalizados só para mostrar uma coluna comparável)
            cands: list[Candidate] = []
            for i in ranked:
                c = self.chunks[i]
                # FAIL-CLOSED: tenant informado exige match exato; sem rótulo = negado.
                if tenant is not None and c.meta.get("tenant") != tenant:
                    continue
                cands.append(Candidate(
                    chunk_id=c.id, doc_id=c.doc_id, text=c.text, meta=c.meta,
                    dense=nd[i], lexical=nl[i], fused=(nd[i] + nl[i]) / 2,
                    embedding=self.embeddings[i],
                ))
                if len(cands) >= k:
                    break
            set_output(cur, {"candidatos": [c.chunk_id for c in cands]})
            return cands
