#!/usr/bin/env python3
"""Rotating backup for settings.json into ~/.nano-backups."""

import json
import shutil
from datetime import datetime
from pathlib import Path

MAX_BACKUPS = 10

def backup() -> None:
    cfg = json.loads(Path("settings.json").read_text())
    backup_dir = Path(cfg["developer_environment"]["backups_directory"]).expanduser()
    backup_dir.mkdir(parents=True, exist_ok=True)

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dest = backup_dir / f"settings_{stamp}.json"
    shutil.copy("settings.json", dest)

    files = sorted(backup_dir.glob("settings_*.json"))
    for old in files[:-MAX_BACKUPS]:
        old.unlink()
        print(f"🗑️  Pruned old backup: {old.name}")

    print(f"✅ Backed up to {dest}")

if __name__ == "__main__":
    backup()
