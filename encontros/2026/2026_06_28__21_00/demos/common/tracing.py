"""Tracing opcional das PoCs para um Phoenix local.

Ative com PHOENIX_TRACING=1. Sem essa variável (ou sem as dependências), este
módulo vira no-op e as PoCs continuam com o mesmo comportamento.
"""

from __future__ import annotations

import functools
import json
import os
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Callable, Iterator

_TRACER = None


def enabled() -> bool:
    return os.environ.get("PHOENIX_TRACING", "0") == "1"


def banner() -> str:
    """Linha didática para o terminal: explica SE, COMO e ONDE os passos são salvos."""
    if enabled():
        endpoint = os.environ.get(
            "PHOENIX_COLLECTOR_ENDPOINT", "http://127.0.0.1:6006/v1/traces"
        )
        proj = os.environ.get("PHOENIX_PROJECT", "grupo-estudos-rag")
        ui = endpoint.split("/v1/")[0]
        return (
            "🔭 observabilidade: tracing LIGADO\n"
            f"   • cada passo (embed, retrieve, rerank, generate...) vira um 'span'\n"
            f"   • enviados para o Phoenix em {endpoint} (projeto '{proj}')\n"
            f"   • abra a UI em {ui} | dados locais ficam em ./.phoenix/ (não versionado)"
        )
    return (
        "🔭 observabilidade: tracing DESLIGADO (rodando normal)\n"
        "   • para ver cada passo no Phoenix: 'make phoenix-start' e rode com "
        "PHOENIX_TRACING=1\n"
        "   • sem isso, nada é enviado a lugar nenhum — as PoCs só imprimem no terminal"
    )


def _safe(value: Any) -> str:
    def default(obj: Any) -> str:
        return f"<{type(obj).__name__}>"

    try:
        return json.dumps(value, ensure_ascii=False, default=default)
    except Exception:
        return repr(value)


def _get_tracer():
    global _TRACER
    if _TRACER is not None:
        return _TRACER

    # Evita que o Phoenix tente persistir em ~/.phoenix. Mantém tudo autocontido
    # na pasta do encontro, inclusive em ambientes com HOME somente-leitura.
    meeting_dir = Path(__file__).resolve().parents[2]
    os.environ.setdefault("PHOENIX_WORKING_DIR", str(meeting_dir / ".phoenix"))

    from phoenix.otel import register

    provider = register(
        project_name=os.environ.get("PHOENIX_PROJECT", "grupo-estudos-rag"),
        endpoint=os.environ.get(
            "PHOENIX_COLLECTOR_ENDPOINT",
            "http://127.0.0.1:6006/v1/traces",
        ),
        protocol="http/protobuf",
        batch=False,
        verbose=False,
    )
    _TRACER = provider.get_tracer("grupo-estudos.pocs")
    return _TRACER


@contextmanager
def span(
    name: str,
    *,
    kind: str = "CHAIN",
    inputs: Any = None,
    attributes: dict[str, Any] | None = None,
) -> Iterator[Any | None]:
    """Cria um span OpenInference ou não faz nada quando tracing está desligado."""
    if not enabled():
        yield None
        return

    try:
        from openinference.semconv.trace import SpanAttributes

        tracer = _get_tracer()
        with tracer.start_as_current_span(name) as current:
            current.set_attribute(SpanAttributes.OPENINFERENCE_SPAN_KIND, kind)
            if inputs is not None:
                current.set_attribute(SpanAttributes.INPUT_VALUE, _safe(inputs))
                current.set_attribute(SpanAttributes.INPUT_MIME_TYPE, "application/json")
            for key, value in (attributes or {}).items():
                if value is not None:
                    current.set_attribute(key, value)
            yield current
    except Exception as exc:
        # Observabilidade nunca pode derrubar a demonstração principal.
        print(f"[phoenix] tracing indisponível: {exc}")
        yield None


def set_output(current: Any | None, value: Any) -> None:
    if current is None:
        return
    from openinference.semconv.trace import SpanAttributes

    current.set_attribute(SpanAttributes.OUTPUT_VALUE, _safe(value))
    current.set_attribute(SpanAttributes.OUTPUT_MIME_TYPE, "application/json")


def traced(name: str, *, kind: str = "CHAIN") -> Callable:
    """Decorator simples para criar spans-raiz nas execuções das PoCs."""
    def decorate(fn: Callable) -> Callable:
        @functools.wraps(fn)
        def wrapped(*args, **kwargs):
            visible_args = [repr(a)[:500] for a in args if type(a).__name__ != "Client"]
            with span(
                name,
                kind=kind,
                inputs={"args": visible_args, "kwargs": kwargs},
            ) as current:
                result = fn(*args, **kwargs)
                set_output(current, result if result is not None else {"status": "ok"})
                return result

        return wrapped

    return decorate
