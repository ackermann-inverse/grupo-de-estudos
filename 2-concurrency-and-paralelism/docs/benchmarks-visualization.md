# Visualização e comparação dos benchmarks

Este documento sugere como **rodar** e **visualizar em paralelo** os resultados dos benchmarks das três linguagens.

## 1. Formato de saída

Todos os programas imprimem JSON na forma:

```json
{
  "mode": "sequential",
  "N": 100000,
  "workers": 4,
  "primes": 7649,
  "sum": 4116688679,
  "time": 0.27
}
```

### Convenção de nomes sugerida

Crie uma pasta `results/` na raiz e salve:

- `results/node-seq.json`
- `results/node-concurrent.json`
- `results/node-parallel.json`
- `results/python-seq.json`
- `results/python-threads.json`
- `results/python-processes.json`
- `results/go-seq.json`
- `results/go-concurrent.json`
- `results/go-parallel.json`

## 2. Rodando todos os benchmarks

Exemplo de script (bash) para rodar todos os modos com o mesmo `N`:

```bash
#!/usr/bin/env bash
set -euo pipefail

N=${N:-100000}
WORKERS=${WORKERS:-4}

mkdir -p results

echo "Rodando Node..."
( cd node && N=$N WORKERS=$WORKERS node src/benchmark.sequential.js )  > ../results/node-seq.json
( cd node && N=$N WORKERS=$WORKERS node src/benchmark.concurrent.js )  > ../results/node-concurrent.json
( cd node && N=$N WORKERS=$WORKERS node src/benchmark.parallel.js )   > ../results/node-parallel.json

echo "Rodando Python..."
( cd python && N=$N WORKERS=$WORKERS python src/benchmark_sequential.py )   > ../results/python-seq.json
( cd python && N=$N WORKERS=$WORKERS python src/benchmark_threads.py )      > ../results/python-threads.json
( cd python && N=$N WORKERS=$WORKERS python src/benchmark_processes.py )    > ../results/python-processes.json

echo "Rodando Go..."
( cd go && N=$N WORKERS=$WORKERS go run ./src/benchmark_sequential.go )   > ../results/go-seq.json
( cd go && N=$N WORKERS=$WORKERS go run ./src/benchmark_concurrent.go )   > ../results/go-concurrent.json
( cd go && N=$N WORKERS=$WORKERS go run ./src/benchmark_parallel.go )     > ../results/go-parallel.json

echo "Benchmarks concluídos. Resultados em ./results"
```

## 3. Consolidação simples em tabela Markdown

Uma abordagem simples é usar um pequeno script em Python para ler todos os JSONs e gerar uma tabela Markdown com tempos e speedups.

Exemplo (não incluído como arquivo separado, mas fácil de criar):

```python
import json
from pathlib import Path

base = Path("results")
files = [
    "node-seq.json", "node-concurrent.json", "node-parallel.json",
    "python-seq.json", "python-threads.json", "python-processes.json",
    "go-seq.json", "go-concurrent.json", "go-parallel.json",
]

rows = []
for name in files:
    data = json.loads((base / name).read_text())
    lang, mode = name.split("-", 1)
    mode = mode.replace(".json", "")
    rows.append((lang, mode, data["time"], data["primes"], data["sum"]))

print("| Linguagem | Modo | Tempo (s) | Primos | Soma |")
print("|-----------|------|-----------|--------|------|")
for lang, mode, t, primes, total in rows:
    print(f"| {lang} | {mode} | {t:.4f} | {primes} | {total} |")
```

## 4. Ferramentas open‑source para centralizar benchmarks

Você pode ir além do script caseiro e usar ferramentas existentes:

### 4.1 `hyperfine` (CLI)

- Ferramenta de benchmarking de linha de comando.
- Roda comandos múltiplas vezes, mede tempo e gera estatísticas.
- Pode ser usada para validar os tempos observados.

Uso básico:

```bash
hyperfine   'cd node && N=100000 node src/benchmark.sequential.js'   'cd node && N=100000 WORKERS=4 node src/benchmark.parallel.js'
```

### 4.2 Jupyter Notebook + Pandas/Matplotlib

- Carregue todos os JSONs da pasta `results/` em um DataFrame.
- Gere gráficos de barras comparando:
  - tempo por linguagem e modo;
  - speedup vs modo sequencial.

### 4.3 Grafana / Loki / Prometheus (para setups mais elaborados)

Se você quiser algo mais “enterprise”:

- Envie os resultados JSON para um endpoint que grave em um time‑series DB (Prometheus, InfluxDB, etc.).
- Configure dashboards no **Grafana** para:
  - comparar tempos ao longo de várias execuções;
  - ver como mudanças de código impactam o desempenho;
  - acompanhar speedups por branch/commit.

Isso é provavelmente overkill para a oficina, mas funciona bem se você quiser transformar os benchmarks em um “laboratório contínuo”.

## 5. Como exibir os benchmarks em paralelo na apresentação

Sugestão de layout de slide:

1. **Tabela geral**: uma tabela com colunas:
   - Linguagem
   - Modo (seq / conc / paralelo)
   - Tempo (s)
   - Speedup vs seq
2. **Gráfico de barras**:
   - Eixo X: linguagem + modo.
   - Eixo Y: tempo em segundos (quanto menor, melhor).
3. **Gráfico de barras de speedup**:
   - Eixo X: linguagem.
   - Eixo Y: speedup do modo paralelo vs seq.

Exemplo de narrativa:

- Primeiro, mostrar a tabela.
- Depois, destacar:
  - Em I/O‑bound (teoria), por que concorrência brilha e paralelismo pouco ajuda.
  - Em CPU‑bound (nos testes), por que concorrência “pura” quase não melhora (e às vezes piora).
  - Como cada linguagem chega ao modo paralelo (workers/processes/goroutines).

## 6. Conectando com o fluxo de requests concorrentes

Você pode relembrar o diagrama MMD de requests concorrentes e explicar:

- Nos benchmarks, **não há I/O externo**, mas o padrão de “disparar tarefas e depois coletar resultados” é o mesmo:
  - Em Node: você dispara promises e depois faz `Promise.all`.
  - Em Python: `futures = executor.submit(...);` e depois `f.result()` ou `as_completed`.
  - Em Go: você dispara goroutines e sinaliza conclusão via `WaitGroup` ou channels.

Isso fecha o ciclo entre:

1. Conceito teórico (concorrência vs paralelismo).
2. Fluxo de requests concorrentes (quem dispara, quem espera, quem avisa).
3. Benchmark CPU‑bound com os três modos em cada linguagem.

