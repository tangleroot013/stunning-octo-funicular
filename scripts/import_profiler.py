#!/usr/bin/env python3
"""Profile cold import time for every top-level module in src/."""

import importlib
import sys
import time
from pathlib import Path

def profile() -> None:
    times = []
    for py in sorted(Path("src").rglob("__init__.py")):
        mod = ".".join(py.relative_to("src").parent.parts)
        if not mod:
            continue
        t0 = time.perf_counter()
        try:
            importlib.import_module(mod)
            elapsed = (time.perf_counter() - t0) * 1000
            times.append((elapsed, mod))
        except Exception as exc:
            print(f"❌ {mod}: {exc}")
    for elapsed, mod in sorted(times, reverse=True)[:10]:
        print(f"  {elapsed:8.2f}ms  {mod}")
    total = sum(t for t, _ in times)
    print(f"\nTotal: {total:.1f}ms across {len(times)} modules")

if __name__ == "__main__":
    profile()
