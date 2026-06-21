"""Utilidades de texto e retrieval implementadas à mão (sem framework).

O ponto pedagógico é justamente NÃO esconder estas operações:
    - tokenização e contagem aproximada de tokens;
    - chunking;
    - similaridade de cosseno (retrieval denso);
    - BM25 (retrieval lexical/esparso);
    - Reciprocal Rank Fusion (busca híbrida).

(Diversidade/MMR é tema da extensão; ver ../../parte-2-rag-engineering/.)

Cada uma tem limitações declaradas no docstring. Em produção você provavelmente
usaria um vector DB + um search engine; aqui o objetivo é entender o que essas
caixas pretas fazem por baixo.
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass

_TOKEN_RE = re.compile(r"\w+", re.UNICODE)


def tokenize(text: str) -> list[str]:
    """Tokenização ingênua: minúsculas + sequências alfanuméricas (mantém acentos)."""
    return _TOKEN_RE.findall(text.lower())


def approx_tokens(text: str) -> int:
    """Estimativa GROSSEIRA de tokens (~4 chars/token).

    AVISO: tokenização real depende do tokenizer do modelo (BPE/SentencePiece) e
    varia por idioma. PT-BR costuma gerar mais tokens que EN para o mesmo sentido.
    Use isto só para orçamento aproximado em sala; nunca para faturamento.
    """
    return max(1, round(len(text) / 4))


def cosine(a: list[float], b: list[float]) -> float:
    """Cosseno entre dois vetores. Base do retrieval denso."""
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


def chunk_text(text: str, *, max_tokens: int = 120, overlap_tokens: int = 24) -> list[str]:
    """Chunking por parágrafos com orçamento de tokens e sobreposição.

    Não existe tamanho "certo" universal: chunk grande dilui similaridade, chunk
    pequeno perde contexto (ver README, seção RAG). Aqui usamos parágrafos como
    unidade natural e só quebramos quando estouramos o orçamento.
    """
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    chunks: list[str] = []
    buf: list[str] = []
    buf_tokens = 0
    for para in paragraphs:
        ptok = approx_tokens(para)
        if buf and buf_tokens + ptok > max_tokens:
            chunks.append("\n\n".join(buf))
            # sobreposição: mantém o último parágrafo como cabeça do próximo chunk
            if overlap_tokens > 0 and buf:
                tail = buf[-1]
                buf = [tail]
                buf_tokens = approx_tokens(tail)
            else:
                buf, buf_tokens = [], 0
        buf.append(para)
        buf_tokens += ptok
    if buf:
        chunks.append("\n\n".join(buf))
    return chunks


@dataclass
class BM25:
    """BM25 Okapi mínimo. Retrieval lexical: brilha em termos literais (siglas,
    códigos, nomes de produto) onde o denso costuma falhar.

    Referência: Robertson & Zaragoza, "The Probabilistic Relevance Framework:
    BM25 and Beyond" (2009).
    """

    k1: float = 1.5
    b: float = 0.75

    def fit(self, docs_tokens: list[list[str]]) -> "BM25":
        self.docs_tokens = docs_tokens
        self.N = len(docs_tokens)
        self.doc_len = [len(d) for d in docs_tokens]
        self.avgdl = (sum(self.doc_len) / self.N) if self.N else 0.0
        df: dict[str, int] = {}
        for toks in docs_tokens:
            for term in set(toks):
                df[term] = df.get(term, 0) + 1
        # idf com piso em 0 para evitar pesos negativos em termos muito frequentes
        self.idf = {
            t: max(0.0, math.log((self.N - n + 0.5) / (n + 0.5) + 1.0))
            for t, n in df.items()
        }
        self._tf = [self._term_freqs(d) for d in docs_tokens]
        return self

    @staticmethod
    def _term_freqs(tokens: list[str]) -> dict[str, int]:
        tf: dict[str, int] = {}
        for t in tokens:
            tf[t] = tf.get(t, 0) + 1
        return tf

    def score(self, query_tokens: list[str], idx: int) -> float:
        if self.avgdl == 0:
            return 0.0
        tf = self._tf[idx]
        dl = self.doc_len[idx]
        s = 0.0
        for term in query_tokens:
            if term not in tf:
                continue
            idf = self.idf.get(term, 0.0)
            freq = tf[term]
            denom = freq + self.k1 * (1 - self.b + self.b * dl / self.avgdl)
            s += idf * (freq * (self.k1 + 1)) / denom
        return s

    def scores(self, query_tokens: list[str]) -> list[float]:
        return [self.score(query_tokens, i) for i in range(self.N)]


def rrf(rankings: list[list[int]], *, k: int = 60) -> list[tuple[int, float]]:
    """Reciprocal Rank Fusion: combina RANKINGS (não scores), insensível a escala.

    Cada `ranking` é uma lista de ids ordenada do melhor para o pior.
    Score(id) = sum_r 1 / (k + rank_r(id)). Default sensato de busca híbrida.

    Referência: Cormack, Clarke & Buettcher, "Reciprocal Rank Fusion outperforms
    Condorcet and individual rank learning methods" (SIGIR 2009).
    """
    agg: dict[int, float] = {}
    for ranking in rankings:
        for rank, doc_id in enumerate(ranking, start=1):
            agg[doc_id] = agg.get(doc_id, 0.0) + 1.0 / (k + rank)
    return sorted(agg.items(), key=lambda kv: kv[1], reverse=True)


# Nota: MMR (Maximal Marginal Relevance) - seleção relevante E diversa, para evitar
# encher o contexto com quase-duplicatas - é tema da extensão de RAG, não do encontro
# principal. Mantido fora daqui de propósito (era código não exercitado). Ver
# ../../parte-2-rag-engineering/README.md (seção "Diversidade / MMR").


def minmax(values: list[float]) -> list[float]:
    """Normaliza scores para [0,1] (útil ao fundir scores heterogêneos)."""
    if not values:
        return []
    lo, hi = min(values), max(values)
    if hi - lo < 1e-12:
        return [0.0 for _ in values]
    return [(v - lo) / (hi - lo) for v in values]
