"""POC2: pipeline de RAG, filtro por tenant e (opcional) execução real."""

import importlib.util
import os
import sys

import pytest

_POC2 = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                     "demos", "poc2_rag", "rag.py")
_spec = importlib.util.spec_from_file_location("rag", _POC2)
rag = importlib.util.module_from_spec(_spec)
sys.modules["rag"] = rag  # necessário p/ dataclass + annotations
_spec.loader.exec_module(rag)


@pytest.fixture
def client():
    from common.ollama_client import make_client
    return make_client(force_mock=True, quiet=True)


def test_filtro_tenant_bloqueia_cross_tenant(client):
    """Com tenant=mercania, nenhum chunk de atacado-norte pode aparecer."""
    idx = rag.RagIndex(client, include_adversarial=False)
    cands = idx.retrieve("qual o prazo de reembolso?", method="hybrid", k=8,
                         tenant="mercania")
    tenants = {c.meta.get("tenant") for c in cands}
    assert "atacado-norte" not in tenants


def test_sem_filtro_vaza_cross_tenant(client):
    """Sem filtro (tenant=None), o doc de outro cliente pode vazar."""
    idx = rag.RagIndex(client, include_adversarial=False)
    cands = idx.retrieve("qual o prazo de reembolso?", method="hybrid", k=12,
                         tenant=None)
    ids = {c.doc_id for c in cands}
    assert "reembolso-atacado-norte" in ids


def test_chunk_sem_tenant_nao_passa_fail_closed(client):
    """FAIL-CLOSED: um chunk SEM metadado `tenant` não pode passar numa consulta
    tenant-scoped. 'Sem rótulo' é negado, não liberado."""
    idx = rag.RagIndex(client, include_adversarial=False)
    # remove o tenant de um chunk para simular metadado ausente
    alvo = next(c for c in idx.chunks if c.doc_id == "politica-reembolso")
    alvo.meta.pop("tenant", None)
    cands = idx.retrieve("qual o prazo de reembolso?", method="hybrid", k=20,
                         tenant="mercania")
    ids = {c.chunk_id for c in cands}
    assert alvo.id not in ids  # chunk sem tenant foi NEGADO sob filtro
    # sem filtro (tenant=None), ele volta a aparecer
    cands_sem = idx.retrieve("qual o prazo de reembolso?", method="hybrid", k=20,
                             tenant=None)
    assert alvo.id in {c.chunk_id for c in cands_sem}


def test_resposta_cita_fonte_e_acerta_prazo(client):
    res = rag.answer("qual é o prazo de reembolso?", method="hybrid",
                     tenant="mercania", client=client)
    assert "30 dias" in res["resposta"]
    assert any(c.doc_id == "politica-reembolso" for c in res["escolhidos"])


def test_lexical_recupera_codigo_literal(client):
    """BM25 deve recuperar a garantia pelo código SKU literal."""
    idx = rag.RagIndex(client, include_adversarial=False)
    cands = idx.retrieve("garantia do SKU-4471", method="lexical", k=3,
                         tenant="mercania")
    assert any(c.doc_id == "garantia" for c in cands[:2])


# --------------------------------------------------------------------------- #
# Teste de execução REAL: só roda se houver Ollama disponível.                 #
# --------------------------------------------------------------------------- #
def _ollama_disponivel() -> bool:
    from common.ollama_client import _ollama_up, _env
    return _ollama_up(_env("OLLAMA_HOST", "http://localhost:11434"))


@pytest.mark.skipif(not _ollama_disponivel(), reason="Ollama não disponível")
def test_rag_real_responde_grounded():
    from common.ollama_client import make_client
    client = make_client(force_mock=False, quiet=True)
    res = rag.answer("qual é o prazo de reembolso?", method="hybrid",
                     tenant="mercania", client=client)
    assert isinstance(res["resposta"], str) and res["resposta"].strip()
    # a fonte correta deveria estar entre os trechos escolhidos
    assert any(c.doc_id == "politica-reembolso" for c in res["escolhidos"])
