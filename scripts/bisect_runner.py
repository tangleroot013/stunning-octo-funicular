#!/usr/bin/env python3
"""Auto git bisect: find the commit that broke a given test command."""

import subprocess
import sys
from pathlib import Path

def bisect(cmd: list[str]) -> int:
    good = input("Last known good commit (sha/tag): ").strip()
    bad = input("First known bad commit (sha/HEAD): ").strip() or "HEAD"
    subprocess.run(["git", "bisect", "start"], check=True)
    subprocess.run(["git", "bisect", "bad", bad], check=True)
    subprocess.run(["git", "bisect", "good", good], check=True)
    
    test_script = " ".join(cmd) if cmd else "python -m pytest -x"
    bisect_cmd = f"if {test_script}; then exit 0; else exit 1; fi"
    
    result = subprocess.run(["git", "bisect", "run", "sh", "-c", bisect_cmd])
    subprocess.run(["git", "bisect", "reset"], check=True)
    return result.returncode

if __name__ == "__main__":
    sys.exit(bisect(sys.argv[1:]))
