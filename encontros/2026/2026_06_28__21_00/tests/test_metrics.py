"""Métricas puras — math em fixtures pequenos, sem modelo."""

from common import metrics


def test_recall_precision():
    retrieved = ["a", "b", "c", "d"]
    rel = {"a", "c"}
    assert metrics.recall_at_k(retrieved, rel, 4) == 1.0
    assert metrics.recall_at_k(retrieved, rel, 1) == 0.5
    assert metrics.precision_at_k(retrieved, rel, 4) == 0.5
    assert metrics.precision_at_k(retrieved, rel, 2) == 0.5


def test_mrr():
    assert metrics.reciprocal_rank(["x", "y", "a"], {"a"}) == 1 / 3
    assert metrics.reciprocal_rank(["a", "y"], {"a"}) == 1.0
    assert metrics.reciprocal_rank(["x", "y"], {"a"}) == 0.0


def test_ndcg_perfect_and_worst():
    rel = {"a", "b"}
    perfect = metrics.ndcg_at_k(["a", "b", "c"], rel, 3)
    worst = metrics.ndcg_at_k(["c", "d", "a"], rel, 3)
    assert perfect == 1.0
    assert 0.0 < worst < perfect


def test_context_precision_recall():
    ctx = ["a", "x"]
    rel = {"a", "b"}
    assert metrics.context_precision(ctx, rel) == 0.5  # 1 de 2 no contexto é relevante
    assert metrics.context_recall(ctx, rel) == 0.5     # 1 de 2 relevantes no contexto


def test_aggregate_ignores_non_numeric():
    agg = metrics.aggregate([{"recall@k": 1.0, "_x": "skip"}, {"recall@k": 0.0, "_x": "y"}])
    assert agg == {"recall@k": 0.5}
