#!/usr/bin/env python3
"""Autonomous snapshot: create dated backup before risky operations, with rotation."""

import json
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

def snapshot() -> None:
    data = json.loads(Path("settings.json").read_text())
    backup_dir = Path(data["developer_environment"]["backups_directory"]).expanduser()
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    name = f"snapshot_{stamp}"
    
    # Create git bundle
    bundle = backup_dir / f"{name}.bundle"
    subprocess.run(["git", "bundle", "create", str(bundle), "--all"], check=True, capture_output=True)
    
    # Copy working tree (respecting gitignore)
    archive = backup_dir / f"{name}.tar.gz"
    subprocess.run([
        "tar", "-czf", str(archive),
        "--exclude-from=.gitignore",
        "--exclude=.git",
        "."
    ], capture_output=True)
    
    # Rotate: keep last 10
    bundles = sorted(backup_dir.glob("snapshot_*.bundle"))
    archives = sorted(backup_dir.glob("snapshot_*.tar.gz"))
    for old in bundles[:-10]:
        old.unlink()
    for old in archives[:-10]:
        old.unlink()
    
    print(f"✅ Snapshot: {bundle.name} + {archive.name}")
    print(f"   Backups: {len(list(backup_dir.glob('snapshot_*')))} total")

if __name__ == "__main__":
    snapshot()
