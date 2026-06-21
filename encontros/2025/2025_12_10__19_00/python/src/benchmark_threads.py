"""
Benchmark concorrente em Python usando ThreadPoolExecutor.

Devido ao GIL do CPython, este modo não oferece paralelismo real para CPU‑bound.
"""
from __future__ import annotations

import json
import os
import time
from concurrent.futures import ThreadPoolExecutor
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
    workers = int(os.environ.get("WORKERS", "4"))
    data = generate_data(N)
    slice_size = (N + workers - 1) // workers
    slices = [data[i * slice_size : min((i + 1) * slice_size, N)] for i in range(workers)]
    start = time.perf_counter()
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = [executor.submit(process_slice, s) for s in slices]
        results = [f.result() for f in futures]
    total_count = sum(c for c, _ in results)
    total_sum = sum(s for _, s in results)
    elapsed = time.perf_counter() - start
    result = {
        "mode": "concurrent-threads",
        "N": N,
        "workers": workers,
        "primes": total_count,
        "sum": total_sum,
        "time": elapsed,
    }
    print(json.dumps(result))


if __name__ == "__main__":
    main()
