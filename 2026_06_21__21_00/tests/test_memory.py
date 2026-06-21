"""POC3: política de escrita, invalidação, expiração, forget e seleção."""

import importlib.util
import os
import sys

import pytest

_POC3 = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                     "demos", "poc3_memory", "memory.py")
_spec = importlib.util.spec_from_file_location("memory", _POC3)
memory = importlib.util.module_from_spec(_spec)
sys.modules["memory"] = memory  # necessário p/ dataclass + annotations
_spec.loader.exec_module(memory)


@pytest.fixture
def mem():
    from common.ollama_client import make_client
    return memory.Memory(make_client(force_mock=True, quiet=True))


def _write(mem, **kw):
    base = dict(user="u", tenant="t", scope="persistent", kind="fact",
                topic="x", source="user_confirmed", confidence=0.9,
                created="2026-06-01")
    base.update(kw)
    return mem.write(**base)


def test_politica_rejeita_palpite_do_modelo(mem):
    item = _write(mem, source="model_guess", confidence=0.4,
                  text="provavelmente tem um cachorro", topic="pet")
    assert item is None
    assert any(e["op"] == "write_rejected" for e in mem.audit)


def test_conflito_invalida_anterior(mem):
    a = _write(mem, text="Endereço: Rua A", topic="endereco")
    b = _write(mem, text="Endereço: Rua B", topic="endereco", created="2026-06-10")
    assert a.status == "invalidated"
    assert b.status == "active"


def test_expiracao_por_ttl(mem):
    # criado há muito tempo, ttl curto -> expira ao recuperar
    _write(mem, text="oferta antiga", topic="oferta", created="2026-01-01", ttl_days=30)
    out = mem.retrieve(query="oferta antiga", user="u", tenant="t")
    assert out == []  # expirado não é recuperado
    assert any(e["op"] == "expire" for e in mem.audit)


def test_retrieve_ignora_irrelevante(mem):
    _write(mem, text="Prefere notificações pelo canal de e-mail", topic="canal")
    out = mem.retrieve(query="qual a política de garantia da geladeira?",
                       user="u", tenant="t")
    assert out == []


def test_forget_remove_do_usuario(mem):
    _write(mem, text="algo", topic="a")
    _write(mem, text="outra", topic="b")
    removidas = mem.forget_user("u")
    assert removidas == 2
    assert mem.items == []


def test_memoria_data_futura_nao_quebra(mem):
    """Data de criação no futuro (idade negativa) não pode causar divisão por zero."""
    _write(mem, text="nota com data futura", topic="futuro",
           created="2026-12-31")  # depois de HOJE (2026-06-16)
    out = mem.retrieve(query="nota com data futura", user="u", tenant="t",
                       sim_min=0.0)  # garante que passa pelo cálculo de recência
    assert any(i.topic == "futuro" for i in out)  # não levantou exceção e recuperou


def test_dump_all_reintroduz_invalidada(mem):
    """O modo 'recuperar tudo' traz de volta a memória invalidada (o ponto da POC)."""
    _write(mem, text="Endereço: Rua A", topic="endereco")
    _write(mem, text="Endereço: Rua B", topic="endereco", created="2026-06-10")
    dump = mem.retrieve(query="endereço", user="u", tenant="t", strategy="dump_all")
    seletivo = mem.retrieve(query="endereço", user="u", tenant="t")
    assert any(i.status == "invalidated" for i in dump)
    assert all(i.status == "active" for i in seletivo)
