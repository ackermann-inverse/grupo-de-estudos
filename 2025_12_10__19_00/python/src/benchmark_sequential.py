"""
Benchmark sequencial para contagem e soma de primos.

Uso:
    N=100000 python benchmark_sequential.py
"""
from __future__ import annotations

import json
import os
import time

from primes import generate_data, is_prime


def main() -> None:
    n_str = os.environ.get("N", "100000")
    N = int(n_str)
    data = generate_data(N)
    count = 0
    total = 0
    start = time.perf_counter()
    for value in data:
        if is_prime(value):
            count += 1
            total += value
    elapsed = time.perf_counter() - start
    result = {
        "mode": "sequential",
        "N": N,
        "primes": count,
        "sum": total,
        "time": elapsed,
    }
    print(json.dumps(result))


if __name__ == "__main__":
    main()
