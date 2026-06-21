# Demos — Context Engineering, RAG & Memória

Quatro provas de conceito **pequenas, sérias e inspecionáveis**. Sem LangChain/
LlamaIndex: chunking, cosseno, BM25 e RRF estão à mão em [`common/`](common/) para
o conceito ficar visível.

| POC | Pasta | O que demonstra |
|---|---|---|
| **1. Context Assembly** | [`poc1_context_assembly/`](poc1_context_assembly/) | Montagem ingênua × com orçamento/critérios |
| **2. RAG** | [`poc2_rag/`](poc2_rag/) | Pipeline visível; denso/lexical/híbrido; filtro por tenant |
| **3. Memória** | [`poc3_memory/`](poc3_memory/) | Lifecycle: write/retrieve/invalidate/expire/forget |
| **4. Falha** | [`poc4_failure/`](poc4_failure/) | Injeção indireta via RAG + mitigação parcial |

## Pré-requisitos

- **Python 3.10+** (testado em 3.11). Só `requests` e `pytest` (ver
  [`../requirements.txt`](../requirements.txt)).
- **Ollama** para a execução real (modelos locais). Opcional: tudo roda em **MOCK**
  determinístico com `USE_MOCK=1`, sem baixar nada.

## Caminhos de execução

```bash
# 1) tudo de uma vez, a partir da raiz do encontro:
make setup        # venv + deps + (opcional) pull dos modelos
make demo         # roda a POC2 (RAG) — a demo principal
make test         # pytest (modo MOCK, não baixa modelo)

# 2) uma POC isolada:
python demos/poc2_rag/rag.py --query "qual o prazo de reembolso?" --method hybrid

# 3) sem Ollama (valida o pipeline; NÃO é a demo real):
USE_MOCK=1 python demos/poc3_memory/memory.py
```

## Os três modos do modelo

| Modo | Quando usar | O que é |
|---|---|---|
| **Ollama real** | demonstração de verdade | embeddings `nomic-embed-text` + geração `llama3.2` |
| **Fallback automático** | Ollama caiu no meio | os scripts avisam e caem para MOCK |
| **MOCK (`USE_MOCK=1`)** | CI, testes, offline | embeddings por hashing + QA extrativo determinístico |

> O MOCK **não substitui** a execução real. Ele existe para o `make test` passar em
> estado limpo e para depurar plumbing sem download.

## Troubleshooting

| Sintoma | Causa provável | Ação |
|---|---|---|
| `caindo para MOCK` no log | Ollama não está rodando | `ollama serve` em outro terminal; `ollama list` |
| `model 'xxx' not found` | modelo não baixado | `ollama pull nomic-embed-text && ollama pull llama3.2:3b` |
| Lento na primeira execução | carregando modelo na RAM | normal; execuções seguintes são rápidas |
| Pouca RAM (≤8 GB) | `llama3.2:3b` aperta | use `GEN_MODEL=llama3.2:1b` |
| `ModuleNotFoundError: requests` | venv não ativa | `make setup` e ative `.venv` |

Matriz de compatibilidade completa: [`../docs/matriz-compatibilidade.md`](../docs/matriz-compatibilidade.md).
