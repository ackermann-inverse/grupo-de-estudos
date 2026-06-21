"""pytest: torna `demos/` importável e força MOCK (testes não baixam modelo)."""

import os
import sys

os.environ.setdefault("USE_MOCK", "1")

_HERE = os.path.dirname(os.path.abspath(__file__))
_DEMOS = os.path.join(os.path.dirname(_HERE), "demos")
if _DEMOS not in sys.path:
    sys.path.insert(0, _DEMOS)

CORPUS_DIR = os.path.join(_DEMOS, "corpus")
GOLDEN = os.path.join(_DEMOS, "golden", "golden.jsonl")
