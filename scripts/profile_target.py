#!/usr/bin/env python3
"""Profile any Python test or module function and emit a sorted hot-path report."""

import cProfile
import pstats
import sys
import tempfile
from pathlib import Path

def profile(target: str) -> None:
    with tempfile.NamedTemporaryFile(suffix=".prof", delete=False) as tmp:
        cmd = f"import pytest; pytest.main(['-x', '{target}'])" if "test" in target else f"import {target}; pass"
        cProfile.run(cmd, tmp.name)
        stats = pstats.Stats(tmp.name)
        stats.sort_stats("cumtime").print_stats(20)
        Path(tmp.name).unlink()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: profile_target.py <test_file.py::test_name or module.path>")
        sys.exit(1)
    profile(sys.argv[1])
