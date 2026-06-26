# Encontro 5 — Context Engineering, RAG & Memória
# Experiência de execução em poucos comandos. Espelha scripts/.

.DEFAULT_GOAL := help
SHELL := /bin/bash
PY := $(shell [ -x .venv/bin/python ] && echo .venv/bin/python || echo python3)
ENV_FILE := $(if $(wildcard .env),--env-file .env,)
COMPOSE := docker compose -p context-rag-memory -f docker/compose.yml $(ENV_FILE)
PHOENIX_PROJECT ?= context-rag-pocs
TRACE_ENV := PHOENIX_TRACING=1 PHOENIX_PROJECT=$(PHOENIX_PROJECT)

.PHONY: help setup demo test test-real clean poc1 poc2 poc3 poc4 leak \
	phoenix-setup phoenix-start phoenix-stop phoenix-status \
	trace-poc1 trace-poc2 trace-poc3 trace-poc4 trace-leak \
	docker-up docker-down docker-pull docker-phoenix-start docker-phoenix-stop \
	docker-trace-poc1 docker-trace-poc2 docker-trace-poc3 docker-trace-poc4 docker-trace-leak \
	slides-html slides-pdf

help: ## mostra esta ajuda
	@grep -E '^[a-zA-Z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
	 | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-22s\033[0m %s\n", $$1, $$2}'

setup: ## cria venv, instala deps e orienta o download dos modelos
	@bash scripts/setup.sh

demo: ## roda a demo principal (RAG, POC2)
	@bash scripts/demo.sh

test: ## roda os testes em modo MOCK (não baixa modelo)
	@USE_MOCK=1 bash scripts/test.sh

test-real: ## roda os testes usando o Ollama real (precisa estar no ar)
	@USE_MOCK=0 bash scripts/test.sh

clean: ## remove venv, caches e stores de runtime
	@bash scripts/clean.sh

poc1: ## POC1 — context assembly
	@$(PY) demos/poc1_context_assembly/assemble.py

poc2: ## POC2 — RAG
	@$(PY) demos/poc2_rag/rag.py --show-scores

poc3: ## POC3 — memória
	@$(PY) demos/poc3_memory/memory.py

poc4: ## POC4 — injeção indireta
	@$(PY) demos/poc4_failure/attack.py

leak: ## demonstra vazamento cross-tenant (filtro desligado)
	@$(PY) demos/poc2_rag/rag.py --no-tenant-filter

phoenix-setup: ## instala a observabilidade opcional do Phoenix
	@bash scripts/phoenix.sh setup

phoenix-start: ## inicia a UI local do Phoenix em http://127.0.0.1:6006
	@bash scripts/phoenix.sh start

phoenix-stop: ## encerra o Phoenix local
	@bash scripts/phoenix.sh stop

phoenix-status: ## verifica se o Phoenix está online
	@bash scripts/phoenix.sh status

trace-poc1: ## executa POC1 enviando traces ao Phoenix
	@$(TRACE_ENV) $(MAKE) poc1

trace-poc2: ## executa POC2 enviando traces ao Phoenix
	@$(TRACE_ENV) $(MAKE) poc2

trace-poc3: ## executa POC3 enviando traces ao Phoenix
	@$(TRACE_ENV) $(MAKE) poc3

trace-poc4: ## executa POC4 enviando traces ao Phoenix
	@$(TRACE_ENV) $(MAKE) poc4

trace-leak: ## executa vazamento cross-tenant enviando traces ao Phoenix
	@$(TRACE_ENV) $(MAKE) leak

slides-html: ## gera preview HTML dos slides em .generated/
	@mkdir -p ../../../.generated/slides
	@npx --yes @marp-team/marp-cli@latest --theme ../../../assets/marp/grupo-estudos.css slides/slides.md -o ../../../.generated/slides/2026_06_21__21_00.html --allow-local-files

slides-pdf: ## gera PDF dos slides em .generated/ (não versionado)
	@mkdir -p ../../../.generated/slides
	@npx --yes @marp-team/marp-cli@latest --theme ../../../assets/marp/grupo-estudos.css --pdf slides/slides.md -o ../../../.generated/slides/2026_06_21__21_00.pdf --allow-local-files

docker-up: ## sobe Ollama + app via Docker Compose
	@$(COMPOSE) up --build

docker-down: ## derruba o Compose
	@$(COMPOSE) down

docker-pull: ## baixa os modelos no volume do Ollama
	@$(COMPOSE) up -d ollama
	@$(COMPOSE) exec ollama ollama pull $(or $(EMBED_MODEL),nomic-embed-text)
	@$(COMPOSE) exec ollama ollama pull $(or $(GEN_MODEL),llama3.2:1b)

docker-phoenix-start: ## inicia o Phoenix no Compose
	@$(COMPOSE) up -d phoenix

docker-phoenix-stop: ## encerra o Phoenix no Compose
	@$(COMPOSE) stop phoenix

docker-trace-poc1: docker-phoenix-start ## executa POC1 com tracing no Compose
	@$(COMPOSE) run --rm --build -e PHOENIX_TRACING=1 app python demos/poc1_context_assembly/assemble.py

docker-trace-poc2: docker-phoenix-start ## executa POC2 com tracing no Compose
	@$(COMPOSE) run --rm --build -e PHOENIX_TRACING=1 app python demos/poc2_rag/rag.py --show-scores

docker-trace-poc3: docker-phoenix-start ## executa POC3 com tracing no Compose
	@$(COMPOSE) run --rm --build -e PHOENIX_TRACING=1 app python demos/poc3_memory/memory.py

docker-trace-poc4: docker-phoenix-start ## executa POC4 com tracing no Compose
	@$(COMPOSE) run --rm --build -e PHOENIX_TRACING=1 app python demos/poc4_failure/attack.py

docker-trace-leak: docker-phoenix-start ## executa o vazamento com tracing no Compose
	@$(COMPOSE) run --rm --build -e PHOENIX_TRACING=1 app python demos/poc2_rag/rag.py --no-tenant-filter
