"""Rerankers: lexical ordena, MMR diversifica, llm cai p/ lexical em mock, factory valida."""

import pytest
from conftest import CORPUS_DIR


@pytest.fixture
def client():
    from common.ollama_client import make_client
    return make_client(force_mock=True, quiet=True)


@pytest.fixture
def cands(client):
    from common.rag_index import RagIndex
    idx = RagIndex(client, CORPUS_DIR)
    return idx.retrieve("prazo de reembolso e estorno", method="hybrid", k=6, tenant="mercania")


def test_lexical_ordena_por_overlap(client, cands):
    from common.rerankers import lexical_reranker
    out = lexical_reranker("prazo de reembolso", list(cands))
    scores = [c.rerank for c in out]
    assert scores == sorted(scores, reverse=True)


def test_llm_cai_para_lexical_em_mock(client, cands):
    from common.rerankers import lexical_reranker, llm_reranker
    a = [c.chunk_id for c in llm_reranker("prazo de reembolso", list(cands), client=client)]
    b = [c.chunk_id for c in lexical_reranker("prazo de reembolso", list(cands))]
    assert a == b  # em mock, llm == lexical (determinístico)


def test_mmr_diversifica(client, cands):
    from common.rerankers import mmr_reranker
    out = mmr_reranker("reembolso", list(cands), client=client, lambda_=0.5, top_n=3)
    docs = [c.doc_id for c in out[:3]]
    # diversidade: não deve repetir o mesmo doc nos 3 primeiros (corpus tem chunks
    # múltiplos de politica-reembolso; MMR deve evitar empilhá-los)
    assert len(set(docs)) == len(docs)


def test_factory_valida_nome():
    from common.rerankers import get_reranker
    assert callable(get_reranker("llm"))
    with pytest.raises(ValueError):
        get_reranker("inexistente")
