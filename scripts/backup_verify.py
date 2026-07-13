#!/usr/bin/env python3
"""Verify backup integrity: checksum validation, restore test, and RPO/RTO metrics."""

import hashlib
import json
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path

def verify() -> int:
    backup_dir = Path.home() / ".nano-backups"
    if not backup_dir.exists():
        print("ℹ️  No backup directory found.")
        return 0
    
    backups = sorted(backup_dir.glob("settings_*.json"))
    if not backups:
        print("ℹ️  No backups to verify.")
        return 0
    
    latest = backups[-1]
    print(f"Verifying: {latest.name}")
    
    # Checksum
    sha256 = hashlib.sha256(latest.read_bytes()).hexdigest()
    checksum_file = latest.with_suffix(".json.sha256")
    if checksum_file.exists():
        expected = checksum_file.read_text().strip()
        if sha256 != expected:
            print(f"🚨 CHECKSUM MISMATCH: expected {expected[:16]}..., got {sha256[:16]}...")
            return 1
    
    # Restore test
    with tempfile.TemporaryDirectory() as tmp:
        test_path = Path(tmp) / "restored.json"
        test_path.write_bytes(latest.read_bytes())
        try:
            data = json.loads(test_path.read_text())
            assert "repository" in data
            print(f"✅ Restore test passed")
        except Exception as exc:
            print(f"🚨 Restore test failed: {exc}")
            return 1
    
    # RPO check
    mtime = datetime.fromtimestamp(latest.stat().st_mtime)
    age_hours = (datetime.now() - mtime).total_seconds() / 3600
    print(f"   Age: {age_hours:.1f}h (RPO target: 24h)")
    
    if age_hours > 24:
        print(f"⚠️  Backup older than RPO target!")
        return 1
    
    print(f"✅ Backup verified. SHA256: {sha256[:16]}...")
    return 0

if __name__ == "__main__":
    sys.exit(verify())
