# Phoenix local - quickstart de apresentação

O Phoenix é opcional. Sem `PHOENIX_TRACING=1`, as PoCs continuam exatamente no
fluxo original. Os traces ficam locais em `.phoenix/` e não são enviados para um
serviço externo.

## Instalar

```bash
cd encontros/2026/2026_06_28__21_00
make phoenix-setup
```

## Iniciar a interface

```bash
cd encontros/2026/2026_06_28__21_00
make phoenix-start
open http://127.0.0.1:6006
```

## Rodar com tracing

Para o MacBook Air M1 de 8 GB, prefira o modelo de 1B durante a apresentação:

```bash
export USE_MOCK=0
export GEN_MODEL=llama3.2:1b

make trace-retrieval
make trace-rerank
make trace-eval
make trace-observe
```

Se quiser narrar cada etapa também no terminal, combine com `EXPLAIN=1`:

```bash
EXPLAIN=1 make trace-observe
```

O projeto no Phoenix se chama `rag-engineering-pocs`. Abra um trace para mostrar:

- o span-raiz da PoC;
- chamadas `ollama.embed` sem armazenar os vetores completos;
- chamada `ollama.generate` com system prompt, contexto e resposta;
- duração de cada etapa;
- diferença entre retrieval, rerank, avaliação e observabilidade estruturada.

Na POC D, compare o trace JSONL próprio com os spans no Phoenix: o JSONL é uma trilha
aplicacional reprodutível; o Phoenix é a visualização interativa dos passos.

O Phoenix mostra o estado observável da aplicação. Ele não expõe estado interno,
chain-of-thought ou raciocínio oculto do modelo.

## Encerrar

```bash
make phoenix-stop
ollama stop llama3.2:1b
```

## Plano B

Se houver pressão de memória, mantenha o Phoenix aberto e rode as PoCs em MOCK:

```bash
export USE_MOCK=1
make trace-retrieval
make trace-rerank
make trace-eval
make trace-observe
```

O tracing e a estrutura dos spans permanecem visíveis; somente a inferência passa
a ser determinística.

## Medição nesta máquina

Benchmark realizado em um MacBook Air M1 com 8 GB, Discord aberto e Phoenix local:

| Modelo | Memória carregada pelo Ollama | POC D | Memória livre após execução |
|---|---:|---:|---:|
| `llama3.2:1b` | 1,5 GB | 13,6 s | 28% |
| `llama3.2:3b` | 2,5 GB | 16,2 s | 27% |

Os valores variam com navegador, compartilhamento de tela, temperatura e outros
aplicativos. O modelo de 3B cabe, mas o de 1B oferece mais margem para a apresentação.
