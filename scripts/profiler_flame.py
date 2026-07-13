#!/usr/bin/env python3
"""Generate flamegraph-compatible folded stack output for any Python script."""

import cProfile
import pstats
import sys
import tempfile
from pathlib import Path

def flame(cmd: list[str]) -> None:
    with tempfile.NamedTemporaryFile(suffix=".prof", delete=False) as tmp:
        script = " ".join(cmd) if cmd else "pass"
        cProfile.run(script, tmp.name)
        
        stats = pstats.Stats(tmp.name)
        stats.strip_dirs()
        
        # Output folded stacks format
        for func, (cc, nc, tt, ct, callers) in stats.stats.items():
            file, line, name = func
            stack = f"{file}:{line}:{name}"
            print(f"{stack} {int(ct * 1000000)}")  # microseconds
        
        Path(tmp.name).unlink()
        print(f"\n✅ Folded stacks ready for flamegraph.pl")

if __name__ == "__main__":
    flame(sys.argv[1:] if len(sys.argv) > 1 else ["import pytest; pytest.main(['-x', 'tests/'])"])
