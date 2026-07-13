#!/usr/bin/env python3
"""Diff two project snapshots (tar.gz) and report structural changes."""

import tarfile
from pathlib import Path

def diff(snap1: str, snap2: str) -> int:
    def extract_list(path: str) -> set[str]:
        with tarfile.open(path, "r:gz") as tar:
            return {m.name for m in tar.getmembers() if m.isfile()}
    
    a = extract_list(snap1)
    b = extract_list(snap2)
    
    added = b - a
    removed = a - b
    common = a & b
    
    print(f"# Snapshot Diff: {Path(snap1).name} vs {Path(snap2).name}\n")
    print(f"Added:   {len(added)}")
    print(f"Removed: {len(removed)}")
    print(f"Common:  {len(common)}")
    
    if added:
        print(f"\n## Added Files")
        for f in sorted(added)[:20]:
            print(f"  + {f}")
    if removed:
        print(f"\n## Removed Files")
        for f in sorted(removed)[:20]:
            print(f"  - {f}")
    
    return 0

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: snapshot_diff.py <snapshot1.tar.gz> <snapshot2.tar.gz>")
        sys.exit(1)
    sys.exit(diff(sys.argv[1], sys.argv[2]))
