#!/usr/bin/env python3
"""Measure and optimize cold startup time by precompiling and profiling imports."""

import subprocess
import sys
import time
from pathlib import Path

def measure() -> None:
    # Cold start
    t0 = time.perf_counter()
    result = subprocess.run([sys.executable, "-c", "import sys; sys.exit(0)"], capture_output=True)
    python_overhead = (time.perf_counter() - t0) * 1000
    
    # With project imports
    t0 = time.perf_counter()
    result = subprocess.run(
        [sys.executable, "-c", "import sys; sys.path.insert(0, 'src'); import hatch"],
        capture_output=True
    )
    project_overhead = (time.perf_counter() - t0) * 1000
    
    print(f"Python baseline:    {python_overhead:.1f}ms")
    print(f"Project import:     {project_overhead:.1f}ms")
    print(f"Project overhead:   {project_overhead - python_overhead:.1f}ms")
    
    if project_overhead > 500:
        print("\n⚠️  Slow startup detected. Recommendations:")
        print("   1. Run: python -m compileall src/")
        print("   2. Use lazy imports for heavy modules")
        print("   3. Consider __pycache__ warming")
    else:
        print("\n✅ Startup time acceptable.")

if __name__ == "__main__":
    measure()
