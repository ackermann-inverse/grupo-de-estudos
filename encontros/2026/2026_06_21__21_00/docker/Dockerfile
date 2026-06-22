# Imagem mínima para rodar as POCs (cliente Python). O Ollama roda em outro
# serviço (ver compose.yml) — aqui só vai o código + dependências.
FROM python:3.11-slim

WORKDIR /app

# Dependências primeiro (cache de camada)
COPY requirements.txt requirements-observability.txt ./
RUN pip install --no-cache-dir \
    -r requirements.txt \
    -r requirements-observability.txt

# Código das demos e corpus
COPY demos ./demos
COPY tests ./tests

# Fala com o Ollama do serviço vizinho do Compose.
ENV OLLAMA_HOST=http://ollama:11434 \
    GEN_MODEL=llama3.2:1b \
    EMBED_MODEL=nomic-embed-text \
    PHOENIX_PROJECT=context-rag-pocs \
    PHOENIX_COLLECTOR_ENDPOINT=http://phoenix:6006/v1/traces \
    PYTHONUNBUFFERED=1

# Por padrão, roda a demo de RAG. Sobrescreva o comando para outras POCs.
CMD ["python", "demos/poc2_rag/rag.py", "--show-scores"]
