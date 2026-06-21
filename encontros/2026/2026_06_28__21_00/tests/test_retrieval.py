"""RagIndex: métodos de recuperação, fail-closed por tenant e truncamento Matryoshka."""

import os

import pytest
from conftest import CORPUS_DIR


@pytest.fixture
def client():
    from common.ollama_client import make_client
    return make_client(force_mock=True, quiet=True)


def test_metodos_retornam_candidatos(client):
    from common.rag_index import RagIndex
    idx = RagIndex(client, CORPUS_DIR)
    for m in ("dense", "lexical", "hybrid"):
        cands = idx.retrieve("qual o prazo de reembolso?", method=m, k=5, tenant="mercania")
        assert cands and all(c.doc_id for c in cands)


def test_tenant_fail_closed(client):
    from common.rag_index import RagIndex
    idx = RagIndex(client, CORPUS_DIR, include_adversarial=False)
    cands = idx.retrieve("prazo de reembolso", method="hybrid", k=20, tenant="mercania")
    assert all(c.meta.get("tenant") == "mercania" for c in cands)
    assert "reembolso-atacado-norte" not in {c.doc_id for c in cands}
    # sem filtro -> o doc de outro tenant pode aparecer
    leak = idx.retrieve("prazo de reembolso", method="hybrid", k=20, tenant=None)
    assert "reembolso-atacado-norte" in {c.doc_id for c in leak}


def test_chunk_sem_tenant_negado(client):
    from common.rag_index import RagIndex
    idx = RagIndex(client, CORPUS_DIR)
    alvo = next(c for c in idx.chunks if c.doc_id == "politica-reembolso")
    alvo.meta.pop("tenant", None)
    cands = idx.retrieve("prazo de reembolso", method="hybrid", k=20, tenant="mercania")
    assert alvo.id not in {c.chunk_id for c in cands}


def test_matryoshka_trunca_dimensao(client):
    from common.rag_index import RagIndex
    full = RagIndex(client, CORPUS_DIR)
    trunc = RagIndex(client, CORPUS_DIR, embed_dims=64)
    assert len(full.embeddings[0]) > len(trunc.embeddings[0]) == 64
    assert "64d" in trunc.index_version


def test_index_version_muda_com_dims(client):
    from common.rag_index import RagIndex
    a = RagIndex(client, CORPUS_DIR).index_version
    b = RagIndex(client, CORPUS_DIR, embed_dims=128).index_version
    assert a != b
