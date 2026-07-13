#!/usr/bin/env python3
"""Generate a PR review summary: diff stats, changed files, test status."""

import subprocess
from pathlib import Path

def prep() -> None:
    base = subprocess.check_output(["git", "merge-base", "HEAD", "origin/main"], text=True).strip()
    diff = subprocess.check_output(["git", "diff", "--stat", base], text=True)
    files = subprocess.check_output(["git", "diff", "--name-only", base], text=True).splitlines()
    report = [
        "# Review Prep\n",
        f"**Base:** `{base}`\n",
        "## Diff Stats\n",
        "```\n" + diff + "\n```\n",
        "## Changed Files\n",
    ] + [f"- {f}" for f in files] + [
        "\n## Test Status\n",
    ]
    if Path(".last_test_ok").exists():
        report.append("✅ Last test run passed.")
    else:
        report.append("❌ Last test run failed or not recorded.")
    Path("REVIEW_PREP.md").write_text("\n".join(report))
    print("✅ REVIEW_PREP.md generated.")

if __name__ == "__main__":
    prep()
