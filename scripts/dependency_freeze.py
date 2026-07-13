#!/usr/bin/env python3
"""Pin all transitive deps from current venv into requirements-frozen.txt."""

import subprocess
from pathlib import Path

def freeze() -> None:
    result = subprocess.run([sys.executable, "-m", "pip", "freeze"], capture_output=True, text=True)
    Path("requirements-frozen.txt").write_text(result.stdout)
    print("✅ requirements-frozen.txt written.")

if __name__ == "__main__":
    freeze()
