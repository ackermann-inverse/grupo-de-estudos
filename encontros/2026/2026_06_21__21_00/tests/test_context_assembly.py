"""POC1: a montagem com critérios resolve conflito, orça e ordena."""

import importlib.util
import os
import sys

import pytest

_POC1 = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                     "demos", "poc1_context_assembly", "assemble.py")
_spec = importlib.util.spec_from_file_location("assemble", _POC1)
assemble = importlib.util.module_from_spec(_spec)
sys.modules["assemble"] = assemble  # necessário p/ dataclass + annotations
_spec.loader.exec_module(assemble)


@pytest.fixture
def client():
    from common.ollama_client import make_client
    return make_client(force_mock=True, quiet=True)


def test_conflito_invalida_obsoleto():
    """O item obsoleto (reembolso v1) NÃO deve entrar no contexto com critérios."""
    ctx, relatorio = assemble.assemble_budgeted(assemble.ITENS)
    assert "reemb-obsoleto" not in relatorio["incluidos"]
    assert "reemb-vigente" in relatorio["incluidos"]
    # foi registrado como descartado por conflito
    passos = {d["passo"] for d in relatorio["decisoes"]}
    assert "conflito" in passos


def test_orcamento_respeitado():
    _ctx, relatorio = assemble.assemble_budgeted(assemble.ITENS, budget_tokens=90)
    assert relatorio["tokens_usados"] <= 90


def test_proveniencia_apenas_no_budget(client):
    """O contexto ingênuo não tem rótulo de fonte; o com critérios tem."""
    ctx_naive = assemble.assemble_naive(assemble.ITENS)
    ctx_budget, _ = assemble.assemble_budgeted(assemble.ITENS)
    assert "[fonte:" not in ctx_naive
    assert "[fonte:" in ctx_budget


def test_bookend_forte_no_inicio_e_no_fim():
    """O mais forte fica no início e o 2º mais forte no FIM (anti lost-in-the-middle).
    _bookend opera por posição (lista já ordenada por score desc)."""
    ordenado = assemble._bookend(["A", "B", "C", "D"])  # A=mais forte ... D=mais fraco
    assert ordenado[0] == "A"          # mais forte no início
    assert ordenado[-1] == "B"         # 2º mais forte no fim
    assert ordenado == ["A", "C", "D", "B"]
    # casos pequenos não mudam
    assert assemble._bookend(["A", "B"]) == ["A", "B"]


def test_resposta_muda_entre_ingenuo_e_budget(client):
    """Efeito observável: ingênuo expõe 7 dias (obsoleto), budget expõe 30 (vigente)."""
    ctx_naive = assemble.assemble_naive(assemble.ITENS)
    ctx_budget, _ = assemble.assemble_budgeted(assemble.ITENS)
    r_naive = client.generate(assemble.SISTEMA, assemble._prompt(assemble.PERGUNTA, ctx_naive))
    r_budget = client.generate(assemble.SISTEMA, assemble._prompt(assemble.PERGUNTA, ctx_budget))
    assert "7 dias" in r_naive
    assert "30 dias" in r_budget
