"""Rerankers: reordenam o top-k inicial com um sinal mais caro/preciso que o retriever.

Quatro estratégias, da mais leve à mais pesada:

- **lexical**   : sobreposição de termos query×doc. Stand-in barato (o da parte 1).
- **llm**       : LLM local (Ollama) pontua relevância de cada (query, doc). É um
                  "cross-encoder na essência" (lê query e doc juntos) e NÃO baixa nada
                  novo. Padrão deste encontro. Em MOCK cai para lexical (determinístico).
- **cross**     : cross-encoder de verdade via sentence-transformers (OPCIONAL, pesado:
                  ~1–2 GB com torch). Import preguiçoso; instala via requirements-extra.txt.
- **mmr**       : NÃO é relevância, é DIVERSIDADE. Reordena para evitar quase-duplicatas
                  no contexto (Maximal Marginal Relevance).

Todos retornam a lista reordenada e preenchem `c.rerank` (score usado na ordenação).
"""

from __future__ import annotations

import json
import re

from .textutil import mmr as _mmr
from .textutil import tokenize


# --------------------------------------------------------------------------- #
# Lexical (stand-in barato)                                                    #
# --------------------------------------------------------------------------- #
def lexical_reranker(query: str, cands: list, **_) -> list:
    qset = set(tokenize(query))
    for c in cands:
        inter = qset & set(tokenize(c.text))
        c.rerank = len(inter) / (len(qset) or 1)
    return sorted(cands, key=lambda c: c.rerank, reverse=True)


# --------------------------------------------------------------------------- #
# LLM-as-reranker (padrão; cross-encoder na essência, sem download novo)       #
# --------------------------------------------------------------------------- #
_RERANK_SISTEMA = (
    "Você é um avaliador de relevância. Dada uma PERGUNTA e um TRECHO, responda APENAS "
    "um JSON {\"score\": N} onde N é um inteiro de 0 (irrelevante) a 10 (responde "
    "diretamente a pergunta). Considere só o quanto o trecho ajuda a responder."
)


def _parse_score(text: str) -> float:
    m = re.search(r'"?score"?\s*[:=]\s*(\d+(?:\.\d+)?)', text)
    if m:
        return max(0.0, min(10.0, float(m.group(1)))) / 10.0
    # fallback: primeiro número no texto
    m2 = re.search(r"\b(\d+(?:\.\d+)?)\b", text)
    return (min(10.0, float(m2.group(1))) / 10.0) if m2 else 0.0


def llm_reranker(query: str, cands: list, *, client=None, **_) -> list:
    if client is None:
        raise ValueError("llm_reranker requer um client")
    # Em MOCK o LLM canned não produz score; cai para lexical (determinístico).
    if getattr(client, "mode", "mock") == "mock":
        return lexical_reranker(query, cands)
    for c in cands:
        prompt = f"PERGUNTA: {query}\nTRECHO:\n{c.text}\n\nResponda só o JSON."
        try:
            out = client.generate(_RERANK_SISTEMA, prompt, json_format=True)
            c.rerank = _parse_score(out)
        except Exception:
            c.rerank = 0.0
    return sorted(cands, key=lambda c: c.rerank, reverse=True)


# --------------------------------------------------------------------------- #
# Cross-encoder de verdade (OPCIONAL, pesado)                                  #
# --------------------------------------------------------------------------- #
# Modelo multilíngue de MS MARCO funciona com PT-BR. Troque via CROSS_ENCODER_MODEL.
_CROSS_DEFAULT = "cross-encoder/mmarco-mMiniLMv2-L12-H384-v1"
_cross_model = None


def _load_cross(model_name: str):
    global _cross_model
    if _cross_model is not None:
        return _cross_model
    try:
        from sentence_transformers import CrossEncoder  # type: ignore
    except ImportError as e:  # pragma: no cover - caminho opcional
        raise RuntimeError(
            "cross-encoder real exige sentence-transformers + torch. Instale com:\n"
            "  pip install -r requirements-extra.txt\n"
            "ou use o reranker 'llm' (padrão, sem download)."
        ) from e
    _cross_model = CrossEncoder(model_name)
    return _cross_model


def cross_encoder_reranker(query: str, cands: list, *, model_name: str = _CROSS_DEFAULT,
                           **_) -> list:  # pragma: no cover - depende de download pesado
    model = _load_cross(model_name)
    scores = model.predict([(query, c.text) for c in cands])
    for c, s in zip(cands, scores):
        c.rerank = float(s)
    return sorted(cands, key=lambda c: c.rerank, reverse=True)


# --------------------------------------------------------------------------- #
# MMR — diversidade (não é relevância)                                         #
# --------------------------------------------------------------------------- #
def mmr_reranker(query: str, cands: list, *, client=None, lambda_: float = 0.7,
                 top_n: int | None = None, **_) -> list:
    if client is None:
        raise ValueError("mmr_reranker requer um client (para embutir a query)")
    if not cands:
        return cands
    from .rag_index import _truncate  # evita import circular no topo
    dims = len(cands[0].embedding) if cands[0].embedding else None
    qvec = _truncate(client.embed([query])[0], dims)
    cand_vecs = [c.embedding for c in cands]
    order = _mmr(qvec, cand_vecs, lambda_=lambda_, top_n=top_n or len(cands))
    reordered = [cands[i] for i in order]
    # rerank score = posição inversa (só para exibir; MMR é ordenação, não score)
    for rank, c in enumerate(reordered):
        c.rerank = 1.0 - rank / max(1, len(reordered))
    return reordered


RERANKERS = {
    "none": lambda query, cands, **kw: cands,
    "lexical": lexical_reranker,
    "llm": llm_reranker,
    "cross": cross_encoder_reranker,
    "mmr": mmr_reranker,
}


def get_reranker(name: str):
    if name not in RERANKERS:
        raise ValueError(f"reranker desconhecido: {name} (opções: {list(RERANKERS)})")
    return RERANKERS[name]
