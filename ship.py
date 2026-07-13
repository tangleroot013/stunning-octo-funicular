#!/usr/bin/env python3
"""
ship.py — local dev pipeline for CerebroFlow (stunning-octo-funicular)
Usage: .venv/bin/python ship.py "commit message"

Flow: remote-sync check -> artifact check -> pytest+coverage -> coverage
floor check -> stage/commit -> push -> cleanup -> print CI link.
Any failed step halts before touching git.
"""
import re
import shutil
import subprocess
import sys
from pathlib import Path

PROJ = Path(__file__).resolve().parent
VENV_PY = PROJ / ".venv" / "bin" / "python"
PY = str(VENV_PY) if VENV_PY.exists() else "python3"
COV_CACHE = PROJ / ".last_cov_score"

# Directories to skip entirely when scanning for stray files/artifacts.
SKIP_DIRS = {".venv", ".git", "node_modules", "htmlcov", "__pycache__", ".pytest_cache"}


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


def _walk_skip_dirs(root: Path):
    for path in root.rglob("*"):
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        yield path


def verify_remote_sync():
    print("\n=== 0/5 remote sync check ===")
    run(["git", "fetch", "origin"], check=False)
    r = run(["git", "status", "-sb"], check=False)
    status_line = r.stdout.splitlines()[0] if r.stdout else ""
    if "behind" in status_line:
        sys.exit("[halt] local branch is behind origin — run `git pull` first")
    if "diverged" in status_line:
        sys.exit("[halt] local and remote branches have diverged — resolve manually")
    print("[ok] branch in sync with origin")


def check_for_forbidden_artifacts():
    print("\n=== 1/5 pre-flight artifact check ===")
    forbidden_extensions = {".bak", ".backup", ".tmp"}
    text_suffixes = {".py", ".md", ".json", ".toml", ".yml", ".yaml"}
    self_path = Path(__file__).resolve()

    for path in _walk_skip_dirs(PROJ):
        if not path.is_file() or path.resolve() == self_path:
            continue
        if path.suffix in forbidden_extensions:
            sys.exit(f"[halt] loose backup file found: {path.relative_to(PROJ)}")
        if path.suffix in text_suffixes:
            try:
                lines = path.read_text(encoding="utf-8").splitlines()
            except (UnicodeDecodeError, OSError):
                continue
            for line in lines:
                if (line.startswith("<<<<<<< ") or line.rstrip() == "======="
                        or line.startswith(">>>>>>> ")):
                    sys.exit(f"[halt] unresolved merge markers in: {path.relative_to(PROJ)}")
    print("[ok] no stray backups or merge markers found")


def run_tests():
    print("\n=== 2/5 pytest (with coverage) ===")
    r = run([PY, "-m", "pytest", "-q", "--cov=src", "--cov-report=term-missing"], check=False)
    if r.returncode != 0:
        (PROJ / ".last_test_ok").unlink(missing_ok=True)
        sys.exit("[halt] tests failing — fix before shipping")
    print("[ok] all tests passed")
    return r.stdout


def enforce_coverage_floor(pytest_output: str):
    print("\n=== 3/5 coverage floor check ===")
    match = re.search(r"^TOTAL\s+\d+\s+\d+\s+(\d+)%", pytest_output, re.MULTILINE)
    if not match:
        print("[warn] could not parse coverage percentage, skipping floor check")
        return

    current = float(match.group(1))

    if COV_CACHE.exists():
        try:
            last = float(COV_CACHE.read_text().strip())
            if current < last:
                sys.exit(f"[halt] coverage dropped from {last}% to {current}% — fix before shipping")
            print(f"[ok] coverage maintained or improved: {current}% (was {last}%)")
        except ValueError:
            print("[warn] .last_cov_score was corrupt, resetting")

    COV_CACHE.write_text(str(current))


def check_dirty():
    print("\n=== 4/5 git status ===")
    r = run(["git", "status", "--porcelain"])
    if not r.stdout.strip():
        sys.exit("[halt] nothing to commit — working tree clean")
    print(r.stdout)


def commit_and_push(message):
    print("\n=== 5/5 stage + commit + push ===")
    run(["git", "add", "-A"])
    run(["git", "commit", "-m", message])

    new_head = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=PROJ, capture_output=True, text=True
    ).stdout.strip()
    (PROJ / ".last_test_ok").write_text(new_head)
    print(f"[marker] stamped .last_test_ok with {new_head}")

    r = run(["git", "push"], check=False)
    if r.returncode != 0:
        sys.exit("[halt] push failed — check auth/network, commit is local and safe")


def cleanup_pipeline_clutter():
    """Remove runtime clutter. NEVER touches .last_test_ok — the pre-push
    hook depends on it to avoid re-running the full suite."""
    print("\n=== cleanup ===")
    clutter_dirs = {".pytest_cache", "htmlcov", "__pycache__", ".ipynb_checkpoints"}
    clutter_files = {".coverage"}  # .last_test_ok intentionally excluded

    for path in _walk_skip_dirs(PROJ):
        if path.is_dir() and path.name in clutter_dirs:
            shutil.rmtree(path, ignore_errors=True)
            print(f"[clean] removed dir: {path.relative_to(PROJ)}")
        elif path.is_file() and path.name in clutter_files:
            path.unlink(missing_ok=True)
            print(f"[clean] removed file: {path.relative_to(PROJ)}")


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

    verify_remote_sync()
    check_for_forbidden_artifacts()
    pytest_output = run_tests()
    enforce_coverage_floor(pytest_output)
    check_dirty()
    commit_and_push(message)
    cleanup_pipeline_clutter()
    print_ci_link()


if __name__ == "__main__":
    main()
