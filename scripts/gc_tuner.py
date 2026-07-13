#!/usr/bin/env python3
"""Analyze object counts and suggest tuned GC thresholds for long-running processes."""

import gc
import sys
from pathlib import Path

def tune() -> None:
    gc.collect()
    counts = gc.get_count()
    thresholds = gc.get_threshold()
    objects = len(gc.get_objects())
    
    print(f"Current GC: counts={counts}, thresholds={thresholds}, tracked_objects={objects}")
    
    # Suggest tuned thresholds based on object count
    if objects > 500000:
        suggestion = (700, 10, 10)
    elif objects > 100000:
        suggestion = (500, 5, 5)
    else:
        suggestion = (thresholds[0], thresholds[1], thresholds[2])
    
    print(f"\nSuggested thresholds: {suggestion}")
    print(f"Apply with: gc.set_threshold({suggestion[0]}, {suggestion[1]}, {suggestion[2]})")
    
    # Check for uncollectable garbage
    unreachable = gc.garbage
    if unreachable:
        print(f"\n🚨 {len(unreachable)} uncollectable object(s) in gc.garbage")

if __name__ == "__main__":
    tune()
