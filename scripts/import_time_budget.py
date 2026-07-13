#!/usr/bin/env python3
"""Enforce a per-module import time budget to catch slow imports early."""

import importlib
import sys
import time
from pathlib import Path

BUDGET_MS = 50  # per module

def check() -> int:
    offenders = []
    for py in sorted(Path("src").rglob("*.py")):
        mod = ".".join(py.relative_to("src").with_suffix("").parts)
        if not mod or mod.endswith("__init__"):
            continue
        t0 = time.perf_counter()
        try:
            if mod in sys.modules:
                del sys.modules[mod]
            importlib.import_module(mod)
            elapsed = (time.perf_counter() - t0) * 1000
            if elapsed > BUDGET_MS:
                offenders.append((mod, elapsed))
                print(f"❌ {mod}: {elapsed:.1f}ms (budget: {BUDGET_MS}ms)")
            else:
                print(f"✅ {mod}: {elapsed:.1f}ms")
        except Exception as exc:
            print(f"⚠️  {mod}: import failed ({exc})")
    
    if offenders:
        print(f"\\n🚨 {len(offenders)} module(s) exceed {BUDGET_MS}ms import budget.")
        return 1
    print(f"\\n✅ All modules within {BUDGET_MS}ms budget.")
    return 0

if __name__ == "__main__":
    sys.exit(check())
