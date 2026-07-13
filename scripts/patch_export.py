#!/usr/bin/env python3
"""Export uncommitted changes as a timestamped patch with metadata header."""

import subprocess
from datetime import datetime
from pathlib import Path

def export() -> None:
    diff = subprocess.check_output(["git", "diff", "HEAD"], text=True)
    if not diff.strip():
        print("ℹ️  No uncommitted changes.")
        return
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out = Path(f"changes_{stamp}.patch")
    meta = f"# Branch: {subprocess.check_output(['git', 'branch', '--show-current'], text=True).strip()}\\n"
    meta += f"# Generated: {stamp}\\n"
    meta += f"# Files: {len(subprocess.check_output(['git', 'diff', '--name-only', 'HEAD'], text=True).splitlines())}\\n\\n"
    out.write_text(meta + diff)
    print(f"✅ {out} written ({len(diff)} bytes).")

if __name__ == "__main__":
    export()
