# Encontro 5 — Context Engineering, RAG & Memória
# Experiência de execução em poucos comandos. Espelha scripts/.

.DEFAULT_GOAL := help
SHELL := /bin/bash

.PHONY: help setup demo test test-real clean poc1 poc2 poc3 poc4 leak docker-up docker-down

help: ## mostra esta ajuda
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
	 | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'

setup: ## cria venv, instala deps e orienta o download dos modelos
	@bash scripts/setup.sh

demo: ## roda a demo principal (RAG, POC2)
	@bash scripts/demo.sh

test: ## roda os testes em modo MOCK (não baixa modelo)
	@bash scripts/test.sh

test-real: ## roda os testes usando o Ollama real (precisa estar no ar)
	@USE_MOCK=0 bash scripts/test.sh

clean: ## remove venv, caches e stores de runtime
	@bash scripts/clean.sh

poc1: ## POC1 — context assembly
	@.venv/bin/python demos/poc1_context_assembly/assemble.py 2>/dev/null || python demos/poc1_context_assembly/assemble.py

poc2: ## POC2 — RAG
	@.venv/bin/python demos/poc2_rag/rag.py --show-scores 2>/dev/null || python demos/poc2_rag/rag.py --show-scores

poc3: ## POC3 — memória
	@.venv/bin/python demos/poc3_memory/memory.py 2>/dev/null || python demos/poc3_memory/memory.py

poc4: ## POC4 — injeção indireta
	@.venv/bin/python demos/poc4_failure/attack.py 2>/dev/null || python demos/poc4_failure/attack.py

leak: ## demonstra vazamento cross-tenant (filtro desligado)
	@.venv/bin/python demos/poc2_rag/rag.py --no-tenant-filter 2>/dev/null || python demos/poc2_rag/rag.py --no-tenant-filter

docker-up: ## sobe Ollama + app via Docker Compose (caminho alternativo)
	@docker compose -f docker/compose.yml up --build

docker-down: ## derruba o Compose
	@docker compose -f docker/compose.yml down
