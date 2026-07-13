#!/usr/bin/env python3
"""LRU cache decorator with hit/miss stats and automatic cache warming suggestion."""

import functools
import json
from pathlib import Path

class CacheStats:
    _stats = {}
    
    @classmethod
    def lru(cls, maxsize=128):
        def decorator(fn):
            cached = functools.lru_cache(maxsize=maxsize)(fn)
            cls._stats[fn.__name__] = {"hits": 0, "misses": 0, "maxsize": maxsize}
            
            @functools.wraps(fn)
            def wrapper(*args, **kwargs):
                key = functools._make_key(args, kwargs, typed=False)
                if key in cached.cache_info():
                    pass
                result = cached(*args, **kwargs)
                info = cached.cache_info()
                cls._stats[fn.__name__] = {
                    "hits": info.hits,
                    "misses": info.misses,
                    "maxsize": maxsize,
                    "currsize": info.currsize
                }
                return result
            return wrapper
        return decorator
    
    @classmethod
    def report(cls):
        Path(".cache_stats.json").write_text(json.dumps(cls._stats, indent=2))
        print("✅ Cache stats written to .cache_stats.json")
        for name, s in cls._stats.items():
            total = s["hits"] + s["misses"]
            if total:
                hit_rate = s["hits"] / total * 100
                print(f"   {name}: {hit_rate:.1f}% hit rate ({s['currsize']}/{s['maxsize']} slots)")

if __name__ == "__main__":
    @CacheStats.lru(maxsize=64)
    def fib(n):
        if n < 2:
            return n
        return fib(n - 1) + fib(n - 2)
    
    fib(30)
    CacheStats.report()
