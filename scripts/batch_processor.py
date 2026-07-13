#!/usr/bin/env python3
"""Generic batch processor with backpressure and retry logic."""

import time
from collections.abc import Callable
from pathlib import Path

def batch_process(items: list, processor: Callable, batch_size: int = 100, delay: float = 0.0, retries: int = 3):
    results = []
    for i in range(0, len(items), batch_size):
        chunk = items[i:i + batch_size]
        for attempt in range(retries):
            try:
                results.extend(processor(chunk))
                break
            except Exception as exc:
                if attempt == retries - 1:
                    raise
                time.sleep(2 ** attempt)
        if delay:
            time.sleep(delay)
    return results

if __name__ == "__main__":
    def double(nums):
        return [n * 2 for n in nums]
    out = batch_process(list(range(250)), double, batch_size=50, delay=0.01)
    print(f"✅ Processed {len(out)} items in batches")
