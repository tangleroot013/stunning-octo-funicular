#!/usr/bin/env python3
"""Create a clean project tarball respecting .gitignore and .claudeignore."""

import json
import tarfile
from datetime import datetime
from pathlib import Path

def snapshot() -> None:
    ignores = set()
    for f in (".gitignore", ".claudeignore"):
        if Path(f).exists():
            ignores.update(Path(f).read_text().splitlines())
    ignores.update([".git", "__pycache__", "*.pyc", ".venv", ".coverage", "htmlcov", ".pytest_cache", ".mypy_cache", ".ruff_cache"])
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out = Path(f"snapshot_{stamp}.tar.gz")
    with tarfile.open(out, "w:gz") as tar:
        for p in Path(".").rglob("*"):
            if p.is_file():
                rel = str(p.relative_to("."))
                if any(p.match(g.strip()) for g in ignores if g.strip() and not g.startswith("#")):
                    continue
                tar.add(p, arcname=rel)
    size = out.stat().st_size / 1024
    print(f"✅ {out} created ({size:.1f} KB, {len(ignores)} ignore patterns applied)")

if __name__ == "__main__":
    snapshot()
