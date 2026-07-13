#!/usr/bin/env python3
"""Encrypt .env file using Fernet and create .env.enc for safe storage."""

import os
from pathlib import Path

def encrypt() -> int:
    try:
        from cryptography.fernet import Fernet
    except ImportError:
        print("❌ Install cryptography: pip install cryptography")
        return 1
    
    key = os.environ.get("ENV_ENCRYPTION_KEY")
    if not key:
        key = Fernet.generate_key().decode()
        print(f"🔑 Generated key (save this): {key}")
        print("   Set ENV_ENCRYPTION_KEY to use for decryption")
    
    f = Fernet(key.encode())
    env = Path(".env")
    if not env.exists():
        print("ℹ️  No .env file found.")
        return 0
    
    encrypted = f.encrypt(env.read_bytes())
    Path(".env.enc").write_bytes(encrypted)
    print(f"✅ .env → .env.enc ({len(encrypted)} bytes)")
    print("   Remove .env from git: git rm --cached .env && echo '.env' >> .gitignore")
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(encrypt())
