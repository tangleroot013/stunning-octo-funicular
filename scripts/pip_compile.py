#!/usr/bin/env python3
"""Compile requirements.txt into a locked requirements-frozen.txt with hashes."""

import subprocess
import sys
from pathlib import Path

def compile() -> int:
    req = Path("requirements.txt")
    if not req.exists():
        print("❌ requirements.txt not found")
        return 1
    
    print("⏳ Resolving dependencies (this may take a while)...")
    result = subprocess.run([
        sys.executable, "-m", "pip", "install", "pip-tools"
    ], capture_output=True)
    
    result = subprocess.run([
        "pip-compile", "--generate-hashes", "--output-file", "requirements-frozen.txt", "requirements.txt"
    ], capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"❌ pip-compile failed:\\n{result.stderr}")
        return 1
    
    print(f"✅ requirements-frozen.txt generated ({Path('requirements-frozen.txt').stat().st_size} bytes)")
    return 0

if __name__ == "__main__":
    sys.exit(compile())
