"""POC4: a injeção é recuperada; demarcação reduz obediência; guarda de saída pega a canário."""

import importlib.util
import os
import sys

import pytest

_DEMOS = os.path.join(os.path.dirname(os.path.dirname(__file__)), "demos")


def _load(path, name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(_DEMOS, path))
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod  # necessário p/ dataclass + annotations
    spec.loader.exec_module(mod)
    return mod


rag = _load(os.path.join("poc2_rag", "rag.py"), "rag")
attack = _load(os.path.join("poc4_failure", "attack.py"), "attack")


@pytest.fixture
def client():
    from common.ollama_client import make_client
    return make_client(force_mock=True, quiet=True)


def test_documento_envenenado_e_recuperado(client):
    """Mitigar não conserta retrieval: o doc envenenado ainda entra no contexto."""
    idx = rag.RagIndex(client, include_adversarial=True)
    cands = idx.retrieve(attack.QUERY, method="hybrid", k=6, tenant="mercania")
    assert any(c.doc_id == "doc-envenenado" for c in cands[:3])


def test_ingenuo_obedece_mitigado_nao(client):
    idx = rag.RagIndex(client, include_adversarial=True)
    cands = idx.retrieve(attack.QUERY, method="hybrid", k=6, tenant="mercania")

    resp_naive = client.generate(attack.SISTEMA_INGENUO,
                                 f"CONTEXTO:\n{attack.naive_context(cands)}\n\n"
                                 f"PERGUNTA: {attack.QUERY}\nRESPOSTA:")
    resp_mit = client.generate(attack.SISTEMA_MITIGADO,
                               f"CONTEXTO:\n{attack.mitigated_context(cands)}\n\n"
                               f"PERGUNTA: {attack.QUERY}\nRESPOSTA:")
    # No MOCK, instrução fora da cerca é obedecida; dentro da cerca, não.
    assert attack.CANARIO in resp_naive.upper()
    assert attack.CANARIO not in resp_mit.upper()


def test_fence_close_nao_vaza_no_texto_extraido():
    """A tag de fechamento da cerca não pode entrar no texto que o mock extrai."""
    from common.ollama_client import FENCE_CLOSE, FENCE_OPEN, _mock_generate
    prompt = (
        "CONTEXTO:\n"
        f"{FENCE_OPEN}\n"
        "[fonte: doc-x] o prazo de reembolso vigente é de 30 dias corridos\n"
        f"{FENCE_CLOSE}\n\n"
        "PERGUNTA: qual o prazo de reembolso?\nRESPOSTA:"
    )
    resp = _mock_generate("sistema", prompt)
    assert "30 dias" in resp
    assert FENCE_CLOSE not in resp and FENCE_OPEN not in resp
    assert "doc-x" in resp  # citou a fonte do bloco


def test_guarda_de_saida_bloqueia_canario():
    ok, shown = attack.output_guard("resposta com PWNED-7Q2 vazado")
    assert ok is False and "BLOQUEADO" in shown
    ok2, shown2 = attack.output_guard("resposta limpa")
    assert ok2 is True and shown2 == "resposta limpa"
