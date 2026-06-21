"""Observabilidade: trace serializa, Timer mede, TraceLogger grava JSONL."""

import json

from common.observability import RagTrace, Timer, TraceLogger


def test_trace_serializa():
    t = RagTrace(query="q", method="hybrid", tenant="mercania", top_k=3,
                 index_version="nomic@768d-abc", embed_model="nomic", gen_model="llama")
    obj = json.loads(t.to_json())
    assert obj["query"] == "q" and obj["index_version"] == "nomic@768d-abc"


def test_timer_mede_etapas():
    timer = Timer()
    with timer("etapa"):
        sum(range(1000))
    assert "etapa" in timer.spans and timer.total() >= 0


def test_logger_grava_jsonl(tmp_path):
    path = str(tmp_path / "trace.jsonl")
    logger = TraceLogger(path)
    t = RagTrace(query="q", method="dense", tenant=None, top_k=1,
                 index_version="v", embed_model="e", gen_model="g")
    logger.log(t)
    lines = open(path, encoding="utf-8").read().splitlines()
    assert len(lines) == 1 and json.loads(lines[0])["method"] == "dense"


def test_summary_contem_campos_chave():
    t = RagTrace(query="qual o prazo?", method="hybrid", tenant="mercania", top_k=3,
                 index_version="nomic@768d-abc", embed_model="nomic", gen_model="llama",
                 sources=["politica-reembolso"])
    s = TraceLogger.summary(t)
    assert "index_version" in s and "politica-reembolso" in s and "custo" in s
