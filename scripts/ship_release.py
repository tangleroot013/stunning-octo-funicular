#!/usr/bin/env python3
"""Full release orchestrator: bump → changelog → ci → tag → push → verify."""

import json
import subprocess
import sys
from pathlib import Path

def run(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess:
    print(f"▶ {' '.join(cmd)}")
    return subprocess.run(cmd, check=check)

def release() -> int:
    data = json.loads(Path("settings.json").read_text())
    ver = data["library"]["version"]
    print(f"🚀 Starting release for v{ver}\n")
    
    # 1. Validate workspace
    if run([sys.executable, "scripts/workspace_audit.py"]).returncode != 0:
        return 1
    
    # 2. Run full CI simulation
    if run([sys.executable, "scripts/ci_simulate.py"]).returncode != 0:
        print("❌ CI simulation failed. Abort.")
        return 1
    
    # 3. Generate changelog
    run([sys.executable, "scripts/generate_changelog.py"])
    
    # 4. Stage everything
    run(["git", "add", "-A"])
    run(["git", "commit", "-m", f"release: v{ver}"])
    
    # 5. Tag and push
    run(["git", "tag", f"v{ver}"])
    run(["git", "push", "origin", "main", "--tags"])
    
    # 6. Verify PyPI slot
    if run([sys.executable, "scripts/pypi_check.py"]).returncode == 0:
        print(f"\n✅ v{ver} released and PyPI slot confirmed.")
    else:
        print(f"\n⚠️  v{ver} tagged but PyPI slot occupied.")
    return 0

if __name__ == "__main__":
    sys.exit(release())
