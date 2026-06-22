"""Cliente mínimo para o runtime local de modelos (Ollama) + um MOCK determinístico.

Por que este arquivo existe:
    As POCs precisam de duas capacidades de um modelo local: gerar embeddings de
    retrieval e gerar texto. Em vez de esconder isso atrás de um framework, falamos
    HTTP direto com o Ollama (`/api/embeddings` e `/api/chat`). Assim o participante
    vê exatamente o que entra e o que sai.

O MOCK (USE_MOCK=1, ou fallback automático quando o Ollama não responde):
    - embeddings determinísticos por *hashing* de termos (similaridade ~ sobreposição
      lexical). NÃO é semântico; serve só para validar o pipeline e rodar os testes
      sem baixar modelo.
    - um "LLM" canned, igualmente determinístico.
    O MOCK NÃO substitui a execução real com modelo local. Ele existe para o
    `make test` passar em estado limpo e para depurar plumbing offline.

Documentação oficial do Ollama (acesso em 2026-06-16):
    - API:        https://github.com/ollama/ollama/blob/main/docs/api.md
    - Embeddings: https://docs.ollama.com/api/embeddings
"""

from __future__ import annotations

import hashlib
import math
import os
import re
from dataclasses import dataclass

from common.tracing import set_output, span

try:
    import requests
except ImportError:  # pragma: no cover - requests só é exigido no caminho real
    requests = None  # type: ignore

_MOCK_DIM = 512
_TOKEN_RE = re.compile(r"\w+", re.UNICODE)


def _env(name: str, default: str) -> str:
    value = os.environ.get(name)
    return value if value not in (None, "") else default


def _tokenize(text: str) -> list[str]:
    return _TOKEN_RE.findall(text.lower())


# --------------------------------------------------------------------------- #
# MOCK determinístico                                                         #
# --------------------------------------------------------------------------- #
def _mock_embed_one(text: str) -> list[float]:
    """Embedding por hashing: cada termo cai em um bucket fixo, com peso tf.

    Resultado: o cosseno entre dois textos aproxima a sobreposição de termos.
    É lexical, não semântico - e isso é dito em voz alta no material.
    """
    vec = [0.0] * _MOCK_DIM
    for tok in _tokenize(text):
        h = int(hashlib.sha1(tok.encode("utf-8")).hexdigest(), 16)
        bucket = h % _MOCK_DIM
        sign = 1.0 if (h // _MOCK_DIM) % 2 == 0 else -1.0
        vec[bucket] += sign
    norm = math.sqrt(sum(v * v for v in vec)) or 1.0
    return [v / norm for v in vec]


_FENCE_OPEN = "<dados_nao_confiaveis>"
_FENCE_CLOSE = "</dados_nao_confiaveis>"
_INJECTION_MARK = "INSTRUCAO-INJETADA:"


def _strip_fenced(prompt: str) -> str:
    """Remove o conteúdo entre marcadores de dados não confiáveis.

    Usado pelo LLM mock para *simular* um modelo que tende a obedecer instruções
    que aparecem como se fossem do sistema/usuário, mas ignora o que está
    claramente demarcado como dado não confiável. É uma simulação - o modelo real
    pode obedecer mesmo assim (ver POC4 e a seção de segurança do README).
    """
    out, depth, i = [], 0, 0
    while i < len(prompt):
        if prompt.startswith(_FENCE_OPEN, i):
            depth += 1
            i += len(_FENCE_OPEN)
        elif prompt.startswith(_FENCE_CLOSE, i):
            depth = max(0, depth - 1)
            i += len(_FENCE_CLOSE)
        else:
            if depth == 0:
                out.append(prompt[i])
            i += 1
    return "".join(out)


_BLOCK_RE = re.compile(r"^\s*\[fonte:\s*([^\]]+)\]\s*(.+)$")


def _extract_question(prompt: str) -> str:
    for line in prompt.splitlines():
        s = line.strip()
        if s.upper().startswith("PERGUNTA"):
            return s.split(":", 1)[-1].strip()
    # fallback: última linha não vazia
    for line in reversed(prompt.splitlines()):
        if line.strip():
            return line.strip()
    return prompt


def _overlap(q_tokens: set, text: str) -> int:
    return len(q_tokens & set(_tokenize(text)))


def _mock_generate(system: str, prompt: str) -> str:
    """LLM mock determinístico = QA EXTRATIVO cru, com simulação de obediência a
    injection. NÃO é semântico; só valida o pipeline.

    1) Obediência: se houver uma INSTRUCAO-INJETADA FORA das cercas de dados não
       confiáveis, o "modelo" obedece (ataque bem-sucedido). Dentro das cercas, não.
    2) QA: escolhe o bloco "[fonte: X] texto" com maior sobreposição lexical com a
       pergunta e devolve o texto citando a fonte. Empate -> bloco que aparece antes.
    """
    # (1) Simulação de obediência a indirect prompt injection.
    visible = _strip_fenced(prompt)
    m = re.search(_INJECTION_MARK + r"\s*(.+)", visible)
    if m:
        return m.group(1).strip()

    q_tokens = set(_tokenize(_extract_question(prompt)))

    # (2a) Blocos rotulados "[fonte: X] ..." podendo abranger várias linhas.
    #      Linhas estruturais (PERGUNTA/CONTEXTO/...) e marcadores de cerca de dados
    #      não confiáveis NÃO entram no texto do bloco. Atenção ao casing: as
    #      palavras-chave são MAIÚSCULAS; as cercas são minúsculas. Por isso a
    #      checagem é feita separadamente, sem `.upper()` para as cercas.
    _STRUCT_KW = ("PERGUNTA", "CONTEXTO", "RESPOSTA", "SISTEMA")
    blocks: list[tuple[str, str]] = []  # (fonte, texto-acumulado)
    for line in prompt.splitlines():
        bm = _BLOCK_RE.match(line)
        if bm:
            blocks.append((bm.group(1).strip(), bm.group(2).strip()))
            continue
        s = line.strip()
        if not (blocks and s):
            continue
        if s.upper().startswith(_STRUCT_KW):
            continue
        if s.startswith(_FENCE_OPEN) or s.startswith(_FENCE_CLOSE):
            continue
        src, txt = blocks[-1]
        blocks[-1] = (src, (txt + " " + s).strip())

    if blocks:
        best_i, best_score = 0, -1
        for i, (_src, text) in enumerate(blocks):
            sc = _overlap(q_tokens, text)
            if sc > best_score:
                best_i, best_score = i, sc
        if best_score <= 0:
            return "Nao sei com base no contexto."
        src, text = blocks[best_i]
        return f"{_best_sentence(q_tokens, text)} [{src}]"

    # (2b) Sem blocos rotulados: melhor "frase" de conteúdo por sobreposição.
    sentences = _split_sentences("\n".join(
        l for l in prompt.splitlines()
        if l.strip() and not l.strip().upper().startswith(
            ("PERGUNTA", "CONTEXTO", "RESPOSTA", "SISTEMA"))
    ))
    best = _best_sentence(q_tokens, " ".join(sentences), raw_sentences=sentences)
    return best if _overlap(q_tokens, best) > 0 else "Nao sei com base no contexto."


def _split_sentences(text: str) -> list[str]:
    parts: list[str] = []
    for line in text.replace(". ", ".\n").splitlines():
        s = line.strip().lstrip("#").strip()
        if s:
            parts.append(s)
    return parts


def _best_sentence(q_tokens: set, text: str, raw_sentences: list[str] | None = None) -> str:
    sentences = raw_sentences or _split_sentences(text)
    best, best_score = "", -1
    for s in sentences:
        sc = _overlap(q_tokens, s)
        if sc > best_score:
            best, best_score = s, sc
    return best.rstrip(".") + "." if best else text


# --------------------------------------------------------------------------- #
# Cliente                                                                      #
# --------------------------------------------------------------------------- #
@dataclass
class Client:
    mode: str  # "ollama" | "mock"
    host: str
    gen_model: str
    embed_model: str
    embed_calls: int = 0   # contadores baratos p/ observabilidade (proxy de custo)
    gen_calls: int = 0

    def embed(self, texts: list[str]) -> list[list[float]]:
        self.embed_calls += len(texts)
        with span(
            "ollama.embed", kind="EMBEDDING",
            inputs={"texts": [t[:300] for t in texts[:5]], "count": len(texts)},
            attributes={"embedding.model_name": self.embed_model, "llm.provider": self.mode},
        ) as cur:
            if self.mode == "mock":
                out = [_mock_embed_one(t) for t in texts]
            else:
                out = []
                for t in texts:
                    r = requests.post(
                        f"{self.host}/api/embeddings",
                        json={"model": self.embed_model, "prompt": t},
                        timeout=120,
                    )
                    r.raise_for_status()
                    out.append(r.json()["embedding"])
            set_output(cur, {"vectors": len(out), "dimensions": len(out[0]) if out else 0})
            return out

    def generate(self, system: str, prompt: str, *, json_format: bool = False) -> str:
        self.gen_calls += 1
        with span(
            "ollama.generate", kind="LLM",
            inputs={"system": system[:300], "prompt": prompt[:800]},
            attributes={"llm.model_name": self.gen_model, "llm.provider": self.mode},
        ) as cur:
            if self.mode == "mock":
                out = _mock_generate(system, prompt)
            else:
                payload = {
                    "model": self.gen_model,
                    "messages": [
                        {"role": "system", "content": system},
                        {"role": "user", "content": prompt},
                    ],
                    "stream": False,
                    "options": {"temperature": 0},
                }
                if json_format:
                    payload["format"] = "json"
                r = requests.post(f"{self.host}/api/chat", json=payload, timeout=300)
                r.raise_for_status()
                out = r.json()["message"]["content"]
            set_output(cur, out)
            return out


def _ollama_up(host: str) -> bool:
    if requests is None:
        return False
    try:
        r = requests.get(f"{host}/api/tags", timeout=3)
        return r.status_code == 200
    except Exception:
        return False


def make_client(*, force_mock: bool | None = None, quiet: bool = False) -> Client:
    """Decide entre Ollama real e MOCK.

    Ordem: argumento explícito > USE_MOCK=1 > Ollama indisponível -> MOCK.
    """
    host = _env("OLLAMA_HOST", "http://localhost:11434")
    gen = _env("GEN_MODEL", "llama3.2:3b")
    emb = _env("EMBED_MODEL", "nomic-embed-text")

    want_mock = force_mock if force_mock is not None else _env("USE_MOCK", "0") == "1"
    if not want_mock and not _ollama_up(host):
        if not quiet:
            print(
                "[aviso] Ollama nao respondeu em "
                f"{host}; caindo para MOCK deterministico. "
                "Isto valida o pipeline, mas NAO e a demonstracao real."
            )
        want_mock = True

    if want_mock:
        return Client(mode="mock", host=host, gen_model="mock", embed_model="mock")
    return Client(mode="ollama", host=host, gen_model=gen, embed_model=emb)


# Constantes exportadas para as POCs reutilizarem nos prompts.
FENCE_OPEN = _FENCE_OPEN
FENCE_CLOSE = _FENCE_CLOSE
INJECTION_MARK = _INJECTION_MARK
