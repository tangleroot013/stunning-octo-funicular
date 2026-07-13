#!/usr/bin/env python3
"""Track peak memory usage of any Python command via tracemalloc."""

import subprocess
import sys
import tempfile
from pathlib import Path

def track(cmd: list[str]) -> int:
    script = f'''
import tracemalloc, sys
tracemalloc.start()
exec(open("{cmd[0]}").read())
current, peak = tracemalloc.get_traced_memory()
print(f"MEMORY_PEAK: {{peak / 1024 / 1024:.2f}} MB")
tracemalloc.stop()
'''
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(script)
        f.flush()
        result = subprocess.run([sys.executable, f.name] + cmd[1:], capture_output=True, text=True)
        for line in result.stdout.splitlines():
            if "MEMORY_PEAK:" in line:
                print(line)
        return result.returncode

if __name__ == "__main__":
    sys.exit(track(sys.argv[1:]))
