#!/usr/bin/env python3
"""Compress logs older than 7 days into dated tar.gz archives and purge originals."""

import gzip
import shutil
from datetime import datetime, timedelta
from pathlib import Path

def archive() -> None:
    cutoff = datetime.now() - timedelta(days=7)
    archived = 0
    for log in Path(".").rglob("*.log"):
        if log.stat().st_mtime < cutoff.timestamp():
            stamp = datetime.fromtimestamp(log.stat().st_mtime).strftime("%Y%m%d")
            out = Path(f"archive/logs_{stamp}.tar.gz")
            out.parent.mkdir(exist_ok=True)
            # Append to existing archive or create new
            import tarfile
            mode = "a" if out.exists() else "w:gz"
            with tarfile.open(out, mode) as tar:
                tar.add(log, arcname=log.name)
            log.unlink()
            print(f"📦 {log.name} → {out}")
            archived += 1
    if archived:
        print(f"✅ Archived {archived} log file(s).")
    else:
        print("ℹ️  No old logs to archive.")

if __name__ == "__main__":
    archive()
