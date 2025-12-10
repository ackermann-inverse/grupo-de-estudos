"""
Funções compartilhadas para o benchmark de concorrência/paralelismo em Python.

Inclui:
* `is_prime(n)`: verificação simples de primalidade.
* `generate_data(n)`: gera `n` números inteiros determinísticos usando um LCG.
"""
from __future__ import annotations

import math


def is_prime(n: int) -> bool:
    """Retorna True se `n` for primo, False caso contrário."""
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    limit = int(math.isqrt(n))
    for i in range(3, limit + 1, 2):
        if n % i == 0:
            return False
    return True


def generate_data(count: int) -> list[int]:
    """Gera uma lista determinística de inteiros usando LCG."""
    data: list[int] = [0] * count
    seed = 42
    for i in range(count):
        seed = (seed * 1664525 + 1013904223) & 0xFFFFFFFF
        data[i] = 100_000 + (seed % 900_000)
    return data
