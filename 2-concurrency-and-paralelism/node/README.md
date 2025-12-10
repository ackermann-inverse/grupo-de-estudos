# Node.js (JavaScript)

Este diretório contém a implementação do benchmark em Node.js usando apenas APIs nativas.

## Scripts

- `npm run start:seq` – modo **sequencial**.
- `npm run start:concurrent` – modo **concorrente** (Promise pool, mesmo event loop).
- `npm run start:parallel` – modo **paralelo** com `worker_threads`.

## Uso com Docker

```bash
cd node
docker build -t node-bench -f Dockerfile.node .

# Sequencial
docker run --rm -e N=100000 node-bench npm run start:seq

# Concorrente (mesmo event loop)
docker run --rm -e N=100000 -e WORKERS=4 node-bench npm run start:concurrent

# Paralelo (workers)
docker run --rm -e N=100000 -e WORKERS=4 node-bench npm run start:parallel
```

Cada execução imprime um JSON com informações do benchmark.
