# Parte 2 — RAG Engineering. Experiência de execução em poucos comandos.

.DEFAULT_GOAL := help
SHELL := /bin/bash
PY := $(shell [ -x .venv/bin/python ] && echo .venv/bin/python || echo python3)
PHOENIX_PROJECT ?= rag-engineering-pocs
TRACE_ENV := PHOENIX_TRACING=1 PHOENIX_PROJECT=$(PHOENIX_PROJECT)

.PHONY: help setup demo test test-real clean retrieval rerank eval sweep observe cross extra docker-up docker-down \
	phoenix-setup phoenix-start phoenix-stop phoenix-status \
	trace-retrieval trace-rerank trace-eval trace-observe \
	docker-phoenix-start docker-phoenix-stop docker-trace-retrieval docker-trace-rerank \
	docker-trace-eval docker-trace-observe slides-html slides-pdf

help: ## mostra esta ajuda
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
	 | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-24s\033[0m %s\n", $$1, $$2}'

setup: ## cria venv, instala deps e orienta o download dos modelos
	@bash scripts/setup.sh

extra: ## instala o cross-encoder REAL (pesado, ~1-2 GB: torch + sentence-transformers)
	@.venv/bin/pip install -r requirements-extra.txt

phoenix-setup: ## instala a observabilidade opcional do Phoenix
	@bash scripts/phoenix.sh setup

phoenix-start: ## inicia a UI local do Phoenix em http://127.0.0.1:6006
	@bash scripts/phoenix.sh start

phoenix-stop: ## encerra o Phoenix local
	@bash scripts/phoenix.sh stop

phoenix-status: ## verifica se o Phoenix está online
	@bash scripts/phoenix.sh status

trace-retrieval: ## POC A com traces no Phoenix
	@$(TRACE_ENV) $(MAKE) retrieval

trace-rerank: ## POC B com traces no Phoenix
	@$(TRACE_ENV) $(MAKE) rerank

trace-eval: ## POC C (avaliação) com traces no Phoenix
	@$(TRACE_ENV) $(MAKE) eval

trace-observe: ## POC D com traces no Phoenix
	@$(TRACE_ENV) $(MAKE) observe

slides-html: ## gera preview HTML dos slides em .generated/
	@mkdir -p ../../../.generated/slides
	@npx --yes @marp-team/marp-cli@latest --theme ../../../assets/marp/grupo-estudos.css slides/slides.md -o ../../../.generated/slides/2026_06_28__21_00.html --allow-local-files

slides-pdf: ## gera PDF dos slides em .generated/ (não versionado)
	@mkdir -p ../../../.generated/slides
	@npx --yes @marp-team/marp-cli@latest --theme ../../../assets/marp/grupo-estudos.css --pdf slides/slides.md -o ../../../.generated/slides/2026_06_28__21_00.pdf --allow-local-files

demo: ## demo principal: harness de avaliação (POC C)
	@bash scripts/demo.sh

test: ## testes em modo MOCK (não baixa modelo)
	@bash scripts/test.sh

test-real: ## testes usando o Ollama real (precisa estar no ar)
	@USE_MOCK=0 bash scripts/test.sh

clean: ## remove venv, caches e stores de runtime
	@bash scripts/clean.sh

retrieval: ## POC A — dense × lexical × híbrido
	@$(PY) demos/poc_a_retrieval/retrieval.py --query "código da entrega econômica"

rerank: ## POC B — reranking por LLM
	@$(PY) demos/poc_b_rerank/rerank.py --reranker llm --query "prazo de reembolso e estorno"

eval: ## POC C — RAG evaluation harness
	@$(PY) demos/poc_c_eval/evaluate.py

sweep: ## POC C — recall@k vs dimensão do embedding (Matryoshka)
	@$(PY) demos/poc_c_eval/evaluate.py --dims-sweep

observe: ## POC D — trace estruturado de uma consulta
	@$(PY) demos/poc_d_observability/observe.py

cross: ## POC B — cross-encoder REAL (requer 'make extra')
	@$(PY) demos/poc_b_rerank/rerank.py --reranker cross --query "garantia do SKU-4471"

docker-up: ## sobe Ollama + app via Docker Compose
	@docker compose -f docker/compose.yml up --build

docker-down: ## derruba o Compose
	@docker compose -f docker/compose.yml down

docker-phoenix-start: ## inicia o Phoenix no Compose
	@docker compose -f docker/compose.yml up -d phoenix

docker-phoenix-stop: ## encerra o Phoenix no Compose
	@docker compose -f docker/compose.yml stop phoenix

docker-trace-retrieval: docker-phoenix-start ## POC A com tracing no Compose
	@docker compose -f docker/compose.yml run --rm --build -e PHOENIX_TRACING=1 app python demos/poc_a_retrieval/retrieval.py --query "código da entrega econômica"

docker-trace-rerank: docker-phoenix-start ## POC B com tracing no Compose
	@docker compose -f docker/compose.yml run --rm --build -e PHOENIX_TRACING=1 app python demos/poc_b_rerank/rerank.py --reranker llm --query "prazo de reembolso e estorno"

docker-trace-eval: docker-phoenix-start ## POC C com tracing no Compose
	@docker compose -f docker/compose.yml run --rm --build -e PHOENIX_TRACING=1 app python demos/poc_c_eval/evaluate.py

docker-trace-observe: docker-phoenix-start ## POC D com tracing no Compose
	@docker compose -f docker/compose.yml run --rm --build -e PHOENIX_TRACING=1 app python demos/poc_d_observability/observe.py
