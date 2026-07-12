#!/usr/bin/env python3
"""
ship.py — local dev pipeline for CerebroFlow (stunning-octo-funicular)
Usage: .venv/bin/python ship.py "commit message"
Runs: pytest -> git status check -> stage -> commit -> push -> print Actions URL
Any failed step halts the pipeline before touching git.
"""
import subprocess
import sys
from pathlib import Path

PROJ = Path(__file__).resolve().parent
VENV_PY = PROJ / ".venv" / "bin" / "python"
PY = str(VENV_PY) if VENV_PY.exists() else "python3"

def run(cmd, cwd=PROJ, check=True):
    print(f"$ {' '.join(cmd)}")
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if r.stdout:
        print(r.stdout)
    if r.stderr:
        print(r.stderr)
    if check and r.returncode != 0:
        sys.exit(f"[halt] command failed: {' '.join(cmd)}")
    return r

def run_tests():
    print("\n=== 1/4 pytest (with coverage) ===")
    r = run([PY, "-m", "pytest", "-q", "--cov=src", "--cov-report=term-missing"], check=False)
    if r.returncode != 0:
        (PROJ / ".last_test_ok").unlink(missing_ok=True)
        sys.exit("[halt] tests failing — fix before shipping")
    (PROJ / ".last_test_ok").write_text(str(subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=PROJ, capture_output=True, text=True
    ).stdout.strip() or "pending"))
    print("[ok] all tests passed (marker written for pre-push hook)")

def check_dirty():
    print("\n=== 2/4 git status ===")
    r = run(["git", "status", "--porcelain"])
    if not r.stdout.strip():
        sys.exit("[halt] nothing to commit — working tree clean")
    print(r.stdout)

def commit_and_push(message):
    print("\n=== 3/4 stage + commit ===")
    run(["git", "add", "-A"])
    run(["git", "commit", "-m", message])

    print("\n=== 4/4 push ===")
    r = run(["git", "push"], check=False)
    if r.returncode != 0:
        sys.exit("[halt] push failed — check auth/network, commit is local and safe")

def print_ci_link():
    r = run(["git", "remote", "get-url", "origin"], check=False)
    url = r.stdout.strip()
    if url.endswith(".git"):
        url = url[:-4]
    if url.startswith("git@github.com:"):
        url = "https://github.com/" + url.split("git@github.com:")[1]
    print(f"\n[done] pushed. CI run: {url}/actions")

def main():
    if len(sys.argv) < 2:
        sys.exit('usage: ship.py "commit message"')
    message = sys.argv[1]

    run_tests()
    check_dirty()
    commit_and_push(message)
    print_ci_link()

if __name__ == "__main__":
    main()
