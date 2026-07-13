#!/usr/bin/env python3
"""Estimate final wheel/sdist size before build by summing src/ + metadata."""

import json
import subprocess
import tempfile
from pathlib import Path

def estimate() -> None:
    data = json.loads(Path("settings.json").read_text())
    pkg = data["library"]["package_name"]
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run(
            [sys.executable, "-m", "build", "--wheel", "--outdir", tmp],
            capture_output=True
        )
        wheels = list(Path(tmp).glob("*.whl"))
        if wheels:
            size = wheels[0].stat().st_size / 1024
            print(f"📦 Estimated wheel size: {size:.1f} KB ({wheels[0].name})")
        else:
            src_size = sum(f.stat().st_size for f in Path("src").rglob("*") if f.is_file())
            print(f"📦 Source estimate: {src_size/1024:.1f} KB (build failed, fallback)")

if __name__ == "__main__":
    import sys
    estimate()
