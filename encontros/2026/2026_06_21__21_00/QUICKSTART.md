# Quickstart

Este guia funciona em qualquer clone do repositório. Execute os comandos a partir
da pasta deste encontro:

```bash
cd encontros/2026/2026_06_21__21_00
```

Use `make help` a qualquer momento para listar os comandos disponíveis.

## Começar sem baixar modelos

Requer Python 3.10+ e `make`. O modo MOCK é determinístico e serve para conhecer e
validar os pipelines:

```bash
make setup
USE_MOCK=1 make test
USE_MOCK=1 make poc2
```

As outras demonstrações seguem o mesmo padrão:

```bash
USE_MOCK=1 make poc1  # montagem de contexto
USE_MOCK=1 make poc3  # ciclo de vida da memória
USE_MOCK=1 make poc4  # prompt injection indireta
USE_MOCK=1 make leak  # falha de isolamento entre tenants
```

## Usar um modelo local com Ollama

Instale o [Ollama](https://ollama.com/download), deixe o servidor em execução e
baixe um modelo de geração e outro de embeddings:

```bash
ollama pull llama3.2:1b
ollama pull nomic-embed-text

USE_MOCK=0 GEN_MODEL=llama3.2:1b make test-real
USE_MOCK=0 GEN_MODEL=llama3.2:1b make poc2
```

`llama3.2:1b` é o padrão leve. Em uma máquina com mais memória, troque por
`llama3.2:3b`. Para manter as escolhas no fluxo `make demo` e no Docker, copie
`.env.example` para `.env` e edite o arquivo.

## Ativar tracing com Phoenix

O tracing é opcional. No fluxo local, instale as dependências uma vez, inicie a UI
e use os targets `trace-*`:

```bash
make phoenix-setup
make phoenix-start
USE_MOCK=1 make trace-poc2
```

Abra <http://127.0.0.1:6006> e selecione o projeto `context-rag-pocs`. Para as
outras PoCs, use `trace-poc1`, `trace-poc3`, `trace-poc4` ou `trace-leak`.

Ao terminar:

```bash
make phoenix-stop
```

Detalhes sobre os spans e limitações estão em
[`docs/observabilidade-phoenix.md`](./docs/observabilidade-phoenix.md).

## Executar com Docker

Este caminho requer Docker com Compose e não exige Python ou Ollama instalados no
host. Os mesmos componentes rodam em containers:

```bash
make docker-pull
make docker-up
```

`make docker-up` executa a demonstração principal. Para tracing, o Make inicia o
Phoenix e executa a PoC no Compose:

```bash
make docker-trace-poc2
```

A UI fica em <http://127.0.0.1:6006>. Também estão disponíveis
`docker-trace-poc1`, `docker-trace-poc3`, `docker-trace-poc4` e
`docker-trace-leak`.

Para usar somente o MOCK no Docker, sem baixar modelos:

```bash
USE_MOCK=1 make docker-trace-poc2
```

Encerre os containers com:

```bash
make docker-down
```

## Solução rápida de problemas

- `python3: command not found`: instale Python 3.10+ ou use o caminho Docker.
- Ollama indisponível: confirme com `curl http://127.0.0.1:11434/api/tags` ou use
  `USE_MOCK=1`.
- Porta `6006` ocupada: encerre o Phoenix anterior com `make phoenix-stop` ou
  `make docker-phoenix-stop`.
- Ambiente inconsistente: rode `make clean && make setup`.
