# Imagem mínima para rodar as POCs (cliente Python). O Ollama roda em outro
# serviço (ver compose.yml) — aqui só vai o código + dependências.
FROM python:3.11-slim

WORKDIR /app

# Dependências primeiro (cache de camada)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Código das demos e corpus
COPY demos ./demos
COPY tests ./tests

# Fala com o Ollama do serviço vizinho do Compose.
ENV OLLAMA_HOST=http://ollama:11434 \
    GEN_MODEL=llama3.2:3b \
    EMBED_MODEL=nomic-embed-text \
    PYTHONUNBUFFERED=1

# Por padrão, roda o harness de avaliação. Sobrescreva para outras POCs.
CMD ["python", "demos/poc_c_eval/evaluate.py"]
