# Matriz de compatibilidade e requisitos

Honestidade primeiro: **"roda em qualquer máquina" não é verdade** sem ressalvas.
Abaixo, a matriz real, os downloads e os tempos **observados em execução** (não
chutados).

## Ambientes

| Ambiente | Caminho | Status | Observação |
|---|---|---|---|
| macOS Apple Silicon (M-series) | Ollama nativo | ✅ testado | ambiente de referência deste material |
| Linux x86_64 | Ollama nativo ou Docker Compose | ✅ esperado | CPU-only ok; não re-testado aqui |
| Windows 10/11 | WSL2 **ou** Docker Desktop | ⚠️ não testado nativamente | use WSL2; veja limitações |
| CPU-only (sem GPU) | qualquer um acima | ✅ testado | é o caminho principal, de propósito |
| ARM64 (Linux) | Ollama nativo | ✅ esperado | imagem Ollama suporta arm64 |
| Sem internet / sem baixar modelo | `USE_MOCK=1` | ✅ testado | valida pipeline; **não** é a demo real |

## Requisitos de hardware

| Modelo de geração | Download | RAM sugerida | Quando usar |
|---|---:|---:|---|
| `llama3.2:1b` | ~1.3 GB | ≥ 6 GB | máquinas modestas, sala com pouca RAM |
| `llama3.2:3b` | ~2.0 GB | ≥ 8 GB | padrão; melhor qualidade de resposta |
| `nomic-embed-text` (embeddings) | ~274 MB | leve | sempre (separado do gerador) |

> Testado em **Apple Silicon, 8 núcleos, 8 GB de RAM, CPU-only**. O `llama3.2:3b`
> roda nessa configuração; em 8 GB ele aperta se houver muitos apps abertos — nesse
> caso, `GEN_MODEL=llama3.2:1b`.

**Download total** do caminho padrão: ~**2,3 GB** (nomic + 3b) ou ~**1,6 GB**
(nomic + 1b). Baixe **antes** do encontro; o tempo depende da sua conexão.

## Tempos observados (Apple Silicon, 8 GB, CPU, `llama3.2:3b`)

| Ação | Tempo aproximado | Nota |
|---|---:|---|
| `make setup` (venv + pip) | ~20–40 s | sem contar download dos modelos |
| `ollama pull` (nomic + 3b) | minutos | depende da conexão (~2,3 GB) |
| POC2 RAG, 1ª execução (cold) | ~13 s | inclui carregar modelo na RAM + embeddings + 1 geração |
| POC1 (modelo quente) | ~6 s | 2 gerações |
| POC3 (modelo quente) | ~8 s | várias gerações |
| `make test` (MOCK) | ~1–6 s | não baixa modelo |
| `make test-real` (Ollama) | ~3 s | modelo já quente |

A **primeira** inferência sempre é mais lenta (carrega o modelo na RAM). As
seguintes são rápidas.

## Como validar o ambiente rapidamente

```bash
make setup
make test            # deve passar (MOCK) sem Ollama
ollama serve &       # se ainda não estiver rodando
ollama pull nomic-embed-text && ollama pull llama3.2:3b
make demo            # RAG real
make test-real       # testes contra o Ollama
```

Se algo falhar, o caminho `USE_MOCK=1` sempre funciona para validar o pipeline.
