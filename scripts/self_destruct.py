#!/usr/bin/env python3
"""Nuke all generated artifacts, caches, and dotfiles to restore a pristine workspace."""

import shutil
from pathlib import Path

TARGETS = [
    ".coverage", ".last_cov_score", ".last_runtime", ".last_test_ok",
    "coverage.json", "audit.json", "type_check.json", "ship-report.json",
    "lint_report.md", "TODO_REPORT.md", "SIZE_REPORT.md", "DEPRECATION_REPORT.md",
    "DEP_TREE.txt", "API_INDEX.md", "RELEASE_NOTES.md", "CHANGELOG.md",
    "OMNIBUS.md", "REVIEW_PREP.md", "DEPENDENCY_GRAPH.md", "health_dashboard.json",
    "schemas.json", "snapshot_*.tar.gz", "requirements-frozen.txt",
    "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache",
    "htmlcov", "build", "dist", "*.egg-info", ".tox",
]

def destruct() -> None:
    removed = 0
    for pattern in TARGETS:
        for p in Path(".").glob(pattern):
            if p.is_dir():
                shutil.rmtree(p, ignore_errors=True)
                print(f"💥 {p}/")
                removed += 1
            elif p.is_file() or p.is_symlink():
                p.unlink()
                print(f"💥 {p}")
                removed += 1
    print(f"\\n✅ Obliterated {removed} artifact(s). Workspace is pristine.")

if __name__ == "__main__":
    destruct()
