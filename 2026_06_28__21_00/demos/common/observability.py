"""Observabilidade mínima de RAG: sem logs estruturados, não dá para debugar.

Para CADA consulta registramos o que importa para reproduzir e diagnosticar:
query, método, top-k, chunks recuperados + scores, fontes, **versão do índice**,
**modelo de embedding**, latência por etapa e um proxy de **custo** (nº de chamadas a
embedding/geração). Em produção isso vira trace OpenTelemetry (GenAI) + dashboards;
aqui é um JSONL inspecionável.
"""

from __future__ import annotations

import json
import time
from contextlib import contextmanager
from dataclasses import asdict, dataclass, field


@dataclass
class RagTrace:
    query: str
    method: str
    tenant: str | None
    top_k: int
    index_version: str
    embed_model: str
    gen_model: str
    candidates: list[dict] = field(default_factory=list)  # {chunk_id, doc_id, dense, lexical, rerank}
    context_chunk_ids: list[str] = field(default_factory=list)
    sources: list[str] = field(default_factory=list)
    answer: str = ""
    latency_ms: dict = field(default_factory=dict)  # {retrieve, rerank, generate, total}
    cost: dict = field(default_factory=dict)  # {embed_calls, gen_calls}

    def to_json(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False)


class Timer:
    """Cronômetro acumulável por etapa: with timer('retrieve'): ..."""

    def __init__(self) -> None:
        self.spans: dict[str, float] = {}

    @contextmanager
    def __call__(self, name: str):
        t0 = time.perf_counter()
        try:
            yield
        finally:
            self.spans[name] = round((time.perf_counter() - t0) * 1000, 1)

    def total(self) -> float:
        return round(sum(self.spans.values()), 1)


class TraceLogger:
    """Escreve traces em JSONL (uma linha por consulta) e/ou imprime resumo."""

    def __init__(self, path: str | None = None) -> None:
        self.path = path
        if path:
            # trunca o arquivo no início da sessão
            open(path, "w", encoding="utf-8").close()

    def log(self, trace: RagTrace) -> None:
        if self.path:
            with open(self.path, "a", encoding="utf-8") as fh:
                fh.write(trace.to_json() + "\n")

    @staticmethod
    def summary(trace: RagTrace) -> str:
        lt = trace.latency_ms
        return (
            f"query={trace.query!r}\n"
            f"  método={trace.method} top_k={trace.top_k} tenant={trace.tenant}\n"
            f"  index_version={trace.index_version} embed={trace.embed_model} gen={trace.gen_model}\n"
            f"  fontes={trace.sources}\n"
            f"  latência_ms={lt} custo={trace.cost}\n"
            f"  resposta={trace.answer[:120]!r}"
        )
