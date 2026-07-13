#!/usr/bin/env python3
"""Template for CPU-bound parallel execution using ProcessPoolExecutor."""

import concurrent.futures
import math
from pathlib import Path

def is_prime(n: int) -> bool:
    if n < 2:
        return False
    for i in range(2, int(math.sqrt(n)) + 1):
        if n % i == 0:
            return False
    return True

def main(numbers: list[int]) -> list[bool]:
    with concurrent.futures.ProcessPoolExecutor() as pool:
        return list(pool.map(is_prime, numbers))

if __name__ == "__main__":
    nums = list(range(100000, 100050))
    results = main(nums)
    print(f"✅ Checked {len(nums)} numbers across {len(set(results))} unique results")
