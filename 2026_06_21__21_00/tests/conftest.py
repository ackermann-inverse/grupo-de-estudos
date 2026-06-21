"""Configuração do pytest: torna `demos/` importável e força o modo MOCK.

Os testes rodam SEM Ollama (USE_MOCK=1), de propósito: precisam passar em estado
limpo, em CI, sem baixar modelo. Há um teste marcado `@pytest.mark.real` que só roda
quando o Ollama está disponível (ver test_rag.py)."""

import os
import sys

os.environ.setdefault("USE_MOCK", "1")

_HERE = os.path.dirname(os.path.abspath(__file__))
_DEMOS = os.path.join(os.path.dirname(_HERE), "demos")
if _DEMOS not in sys.path:
    sys.path.insert(0, _DEMOS)
