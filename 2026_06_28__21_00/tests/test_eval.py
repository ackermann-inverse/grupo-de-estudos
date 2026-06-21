"""Eval harness: roda o golden set em mock e checa as métricas agregadas."""

import importlib.util
import os
import sys

import pytest
from conftest import CORPUS_DIR, GOLDEN

_POC = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                    "demos", "poc_c_eval", "evaluate.py")
_spec = importlib.util.spec_from_file_location("evaluate", _POC)
evaluate = importlib.util.module_from_spec(_spec)
sys.modules["evaluate"] = evaluate
_spec.loader.exec_module(evaluate)


@pytest.fixture
def client():
    from common.ollama_client import make_client
    return make_client(force_mock=True, quiet=True)


def test_golden_carrega():
    golden = evaluate.load_golden(GOLDEN)
    assert len(golden) >= 10
    assert all("relevant_doc_ids" in g and "query" in g for g in golden)


def test_eval_agrega_metricas(client):
    from common.rag_index import RagIndex
    idx = RagIndex(client, CORPUS_DIR)
    golden = evaluate.load_golden(GOLDEN)
    _, agg = evaluate.run(idx, golden, k=5, top=3, reranker="none",
                          client=client, do_answer=True)
    for key in ("recall@k", "precision@k", "mrr", "ndcg@k", "ctx_precision",
                "ctx_recall", "answer_match"):
        assert key in agg
    # com este corpus/golden, o recall@5 deve ser alto mesmo em mock (lexical)
    assert agg["recall@k"] >= 0.8


def _ollama_disponivel() -> bool:
    from common.ollama_client import _env, _ollama_up
    return _ollama_up(_env("OLLAMA_HOST", "http://localhost:11434"))


@pytest.mark.skipif(not _ollama_disponivel(), reason="Ollama não disponível")
def test_eval_real_recall_alto():
    """Execução REAL: o golden set deve ter recall@k alto com nomic-embed-text."""
    from common.ollama_client import make_client
    from common.rag_index import RagIndex
    rc = make_client(force_mock=False, quiet=True)
    golden = evaluate.load_golden(GOLDEN)
    _, agg = evaluate.run(RagIndex(rc, CORPUS_DIR), golden, k=5, top=3,
                          reranker="none", client=rc, do_answer=False)
    assert agg["recall@k"] >= 0.8


def test_dims_sweep_degrada_qualidade(client):
    """Truncar embedding (Matryoshka) não deve MELHORAR recall — só manter/piorar."""
    from common.rag_index import RagIndex
    golden = evaluate.load_golden(GOLDEN)
    full = evaluate.run(RagIndex(client, CORPUS_DIR), golden, k=5, top=3,
                        reranker="none", client=client, do_answer=False)[1]["recall@k"]
    d64 = evaluate.run(RagIndex(client, CORPUS_DIR, embed_dims=64), golden, k=5, top=3,
                       reranker="none", client=client, do_answer=False)[1]["recall@k"]
    assert d64 <= full
