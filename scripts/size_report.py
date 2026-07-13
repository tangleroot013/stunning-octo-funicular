#!/usr/bin/env python3
"""Report line counts and sizes for src/ and tests/."""

from pathlib import Path

def report() -> None:
    lines = ["# Size Report\n", "| Path | Files | Lines | Bytes |", "|------|-------|-------|-------|"]
    for root in ("src", "tests"):
        files = list(Path(root).rglob("*.py")) if Path(root).exists() else []
        total_lines = sum(len(f.read_text().splitlines()) for f in files)
        total_bytes = sum(f.stat().st_size for f in files)
        lines.append(f"| {root}/ | {len(files)} | {total_lines} | {total_bytes} |")
    Path("SIZE_REPORT.md").write_text("\n".join(lines) + "\n")
    print("✅ SIZE_REPORT.md generated.")

if __name__ == "__main__":
    report()
