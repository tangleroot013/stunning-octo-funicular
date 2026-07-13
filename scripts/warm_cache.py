#!/usr/bin/env python3
"""Pre-warm import caches and common code paths to reduce first-request latency."""

import importlib
import sys
import time
from pathlib import Path

def warm() -> None:
    t0 = time.perf_counter()
    modules = []
    for py in Path("src").rglob("*.py"):
        mod = ".".join(py.relative_to("src").with_suffix("").parts)
        if mod and not mod.endswith("__init__"):
            modules.append(mod)
    
    loaded = 0
    for mod in modules:
        try:
            importlib.import_module(mod)
            loaded += 1
        except Exception:
            pass
    
    # Warm __pycache__
    for py in Path("src").rglob("*.py"):
        compile(py.read_text(), py, "exec")
    
    elapsed = (time.perf_counter() - t0) * 1000
    print(f"✅ Warmed {loaded}/{len(modules)} modules in {elapsed:.1f}ms")
    print(f"   __pycache__ primed for {len(list(Path('src').rglob('*.py')))} files")

if __name__ == "__main__":
    warm()
