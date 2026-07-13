#!/usr/bin/env python3
"""Create a dated git bundle backup of the entire repo."""

import subprocess
from datetime import datetime
from pathlib import Path

def backup() -> None:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out = Path(f"backup_{stamp}.bundle")
    subprocess.run(["git", "bundle", "create", str(out), "--all"], check=True)
    size = out.stat().st_size / 1024
    print(f"✅ {out} ({size:.1f} KB) — verify with: git bundle verify {out}")

if __name__ == "__main__":
    backup()
