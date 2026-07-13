#!/usr/bin/env python3
"""Detect weak cryptographic primitives: MD5, SHA1, DES, RSA<2048, ECB mode."""

import ast
import sys
from pathlib import Path

WEAK = {
    "md5": "cryptographic hash (use SHA-256+)",
    "sha1": "cryptographic hash (use SHA-256+)",
    "sha": "ambiguous hash (specify SHA-256)",
    "DES": "symmetric cipher (use AES-GCM)",
    "Blowfish": "symmetric cipher (use AES-GCM)",
    "ECB": "insecure block mode (use GCM or CBC+MAC)",
    "RSA": "check key size >= 2048",
}

def audit() -> int:
    hits = 0
    for py in Path("src").rglob("*.py"):
        tree = ast.parse(py.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.Name) and node.id in WEAK:
                print(f"🚨 {py}:{node.lineno} weak crypto: {node.id} — {WEAK[node.id]}")
                hits += 1
            if isinstance(node, ast.Attribute):
                if node.attr in WEAK:
                    print(f"🚨 {py}:{node.lineno} weak crypto: {node.attr} — {WEAK[node.attr]}")
                    hits += 1
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id in ("hashlib.new", "hasattr"):
                    pass
                # Check for RSA with small key size
                if isinstance(node.func, ast.Name) and node.func.id in ("RSA", "rsa"):
                    for kw in node.keywords:
                        if kw.arg == "key_size" and isinstance(kw.value, ast.Constant):
                            if kw.value.value < 2048:
                                print(f"🚨 {py}:{node.lineno} RSA key_size={kw.value.value} < 2048")
                                hits += 1
    if hits:
        print(f"\n❌ {hits} weak cryptographic primitive(s). Upgrade immediately.")
        return 1
    print("✅ No weak cryptography detected.")
    return 0

if __name__ == "__main__":
    sys.exit(audit())
