#!/usr/bin/env python3
"""Encrypt settings backups with Fernet (reads key from SETTINGS_BACKUP_KEY env)."""

import os
from pathlib import Path

def encrypt() -> int:
    key = os.environ.get("SETTINGS_BACKUP_KEY")
    if not key:
        print("ℹ️  Set SETTINGS_BACKUP_KEY env var to enable encryption.")
        return 0
    
    try:
        from cryptography.fernet import Fernet
    except ImportError:
        print("❌ Install cryptography: pip install cryptography")
        return 1
    
    f = Fernet(key.encode())
    backup_dir = Path.home() / ".nano-backups"
    encrypted = 0
    for bak in backup_dir.glob("settings_*.json"):
        out = bak.with_suffix(".json.enc")
        if out.exists():
            continue
        out.write_bytes(f.encrypt(bak.read_bytes()))
        print(f"🔒 {bak.name} → {out.name}")
        encrypted += 1
    
    print(f"✅ Encrypted {encrypted} backup(s).")
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(encrypt())
