#!/usr/bin/env python3
"""Persistent SQLite-backed function memoizer for expensive operations."""

import functools
import hashlib
import json
import sqlite3
from pathlib import Path

DB = Path(".cache.sqlite")

def memoize(fn):
    DB.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB)
    conn.execute("CREATE TABLE IF NOT EXISTS cache (key TEXT PRIMARY KEY, value TEXT, ts REAL)")
    conn.commit()
    
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        key = hashlib.sha256(json.dumps((fn.__name__, args, kwargs), sort_keys=True).encode()).hexdigest()
        row = conn.execute("SELECT value FROM cache WHERE key = ?", (key,)).fetchone()
        if row:
            return json.loads(row[0])
        result = fn(*args, **kwargs)
        conn.execute("INSERT OR REPLACE INTO cache VALUES (?, ?, julianday('now'))", (key, json.dumps(result)))
        conn.commit()
        return result
    return wrapper

if __name__ == "__main__":
    @memoize
    def slow_add(a, b):
        import time
        time.sleep(0.1)
        return a + b
    print(slow_add(1, 2))  # cold
    print(slow_add(1, 2))  # cached
    print(f"✅ Cache DB: {DB} ({DB.stat().st_size} bytes)")
