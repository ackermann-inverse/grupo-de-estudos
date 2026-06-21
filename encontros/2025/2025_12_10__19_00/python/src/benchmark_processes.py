"""
Benchmark paralelo em Python usando ProcessPoolExecutor.

Este modo cria processos separados para contornar o GIL e obter paralelismo real.
"""
from __future__ import annotations

import json
import os
import time
from concurrent.futures import ProcessPoolExecutor
from typing import Tuple

from primes import generate_data, is_prime


def process_slice(slice_data: list[int]) -> Tuple[int, int]:
    count = 0
    total = 0
    for value in slice_data:
        if is_prime(value):
            count += 1
            total += value
    return count, total


def main() -> None:
    N = int(os.environ.get("N", "100000"))
    workers_env = os.environ.get("WORKERS")
    workers = int(workers_env) if workers_env is not None else None
    data = generate_data(N)
    slice_count = workers if workers is not None else os.cpu_count() or 1
    slice_size = (N + slice_count - 1) // slice_count
    slices = [data[i * slice_size : min((i + 1) * slice_size, N)] for i in range(slice_count)]
    start = time.perf_counter()
    with ProcessPoolExecutor(max_workers=workers) as executor:
        results = list(executor.map(process_slice, slices))
    total_count = sum(c for c, _ in results)
    total_sum = sum(s for _, s in results)
    elapsed = time.perf_counter() - start
    result = {
        "mode": "parallel-processes",
        "N": N,
        "workers": workers or os.cpu_count(),
        "primes": total_count,
        "sum": total_sum,
        "time": elapsed,
    }
    print(json.dumps(result))


if __name__ == "__main__":
    main()
