#!/usr/bin/env python3
"""Singleton connection pool wrapper with lifecycle management."""

import atexit
from pathlib import Path

class Pool:
    _instance = None
    _clients = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            atexit.register(cls._instance.close_all)
        return cls._instance
    
    def get(self, name: str, factory):
        if name not in self._clients:
            self._clients[name] = factory()
            print(f"🔌 New connection: {name}")
        return self._clients[name]
    
    def close_all(self):
        for name, client in self._clients.items():
            if hasattr(client, "close"):
                client.close()
                print(f"🔒 Closed: {name}")
        self._clients.clear()

if __name__ == "__main__":
    pool = Pool()
    def make_db():
        class FakeDB:
            def close(self): pass
        return FakeDB()
    db = pool.get("postgres", make_db)
    db2 = pool.get("postgres", make_db)
    print(f"✅ Same instance: {db is db2}")
