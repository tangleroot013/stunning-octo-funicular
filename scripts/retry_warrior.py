#!/usr/bin/env python3
"""Production-grade retry decorator: exponential backoff, jitter, circuit breaker."""

import functools
import random
import time
from pathlib import Path

class CircuitBreaker:
    _state = "closed"
    _failures = 0
    _last_failure = 0
    threshold = 5
    timeout = 60

def retry(max_attempts=3, backoff=2.0, max_delay=60.0, exceptions=(Exception,), jitter=True):
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            if CircuitBreaker._state == "open":
                if time.time() - CircuitBreaker._last_failure < CircuitBreaker.timeout:
                    raise RuntimeError("Circuit breaker OPEN")
                CircuitBreaker._state = "half-open"
            
            for attempt in range(1, max_attempts + 1):
                try:
                    result = fn(*args, **kwargs)
                    if CircuitBreaker._state == "half-open":
                        CircuitBreaker._state = "closed"
                        CircuitBreaker._failures = 0
                    return result
                except exceptions as exc:
                    CircuitBreaker._failures += 1
                    CircuitBreaker._last_failure = time.time()
                    if CircuitBreaker._failures >= CircuitBreaker.threshold:
                        CircuitBreaker._state = "open"
                        raise RuntimeError(f"Circuit breaker tripped after {CircuitBreaker._failures} failures") from exc
                    
                    if attempt == max_attempts:
                        raise
                    
                    delay = min(backoff ** attempt, max_delay)
                    if jitter:
                        delay *= random.uniform(0.5, 1.5)
                    print(f"⚠️  {fn.__name__} attempt {attempt}/{max_attempts} failed: {exc}. Retrying in {delay:.1f}s...")
                    time.sleep(delay)
        return wrapper
    return decorator

if __name__ == "__main__":
    @retry(max_attempts=3, backoff=1.5)
    def flaky():
        if random.random() < 0.7:
            raise ConnectionError("simulated")
        return "success"
    try:
        print(flaky())
    except Exception as exc:
        print(f"❌ Final failure: {exc}")
