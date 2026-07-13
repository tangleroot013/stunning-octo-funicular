#!/usr/bin/env python3
"""
ship.py - local dev pipeline for CerebroFlow (stunning-octo-funicular)
Usage: .venv/bin/python ship.py "commit message" [--interactive] [--format]
"""
import argparse
import itertools
import re
import shutil
import socket
import subprocess
import sys
import threading
import time
from pathlib import Path

PROJ = Path(__file__).resolve().parent
VENV_PY = PROJ / ".venv" / "bin" / "python"
PY = str(VENV_PY) if VENV_PY.exists() else "python3"
COV_CACHE = PROJ / ".last_cov_score"
RUNTIME_CACHE = PROJ / ".last_runtime"
SELF_PATH = Path(__file__).resolve()

SKIP_DIRS = {".venv", ".git", "node_modules", "htmlcov", "__pycache__", ".pytest_cache"}


class Spinner:
    FRAMES = ["|", "/", "-", "\\"]

    def __init__(self, message="Working"):
        self.message = message
        self.running = False
        self._thread = None

    def _spin(self):
        for frame in itertools.cycle(self.FRAMES):
            if not self.running:
                break
            sys.stdout.write("\r" + frame + " " + self.message + "...")
            sys.stdout.flush()
            time.sleep(0.1)
        sys.stdout.write("\r" + " " * 60 + "\r")
        sys.stdout.flush()

    def __enter__(self):
        self.running = True
        self._thread = threading.Thread(target=self._spin, daemon=True)
        self._thread.start()
        return self

    def __exit__(self, *exc):
        self.running = False
        if self._thread:
            self._thread.join(timeout=0.5)


def run(cmd, cwd=PROJ, check=True, spinner_msg=None):
    print("$ " + " ".join(cmd))
    if spinner_msg:
        with Spinner(spinner_msg):
            r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    else:
        r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if r.stdout:
        print(r.stdout)
    if r.stderr:
        print(r.stderr)
    if check and r.returncode != 0:
        sys.exit("[halt] command failed: " + " ".join(cmd))
    return r


def _walk_skip_dirs(root: Path):
    for path in root.rglob("*"):
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        yield path


def is_online(host="8.8.8.8", port=53, timeout=2) -> bool:
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except OSError:
        return False


def verify_remote_sync():
    print("\n=== 0/9 remote sync check ===")
    if not is_online():
        print("[warn] offline - skipping remote sync check")
        return
    run(["git", "fetch", "origin"], check=False)
    r = run(["git", "status", "-sb"], check=False)
    status_line = r.stdout.splitlines()[0] if r.stdout else ""
    if "behind" in status_line:
        sys.exit("[halt] local branch is behind origin - run git pull first")
    if "diverged" in status_line:
        sys.exit("[halt] local and remote branches have diverged - resolve manually")
    print("[ok] branch in sync with origin")


def interactive_artifact_resolver(stray_file: Path) -> bool:
    print("\n[artifact] Found issue in " + stray_file.name)
    choice = input("Action? [d]elete file / [v]iew in editor / [i]gnore & halt: ").lower().strip()
    if choice == "d":
        stray_file.unlink()
        print("[removed] " + stray_file.name)
        return True
    if choice == "v":
        import os
        editor = os.environ.get("EDITOR", "nano")
        subprocess.run([editor, str(stray_file)])
        return False
    sys.exit("[halt] pipeline stopped by user")


def check_for_forbidden_artifacts(interactive: bool):
    print("\n=== 1/9 pre-flight artifact check ===")
    forbidden_extensions = {".bak", ".backup", ".tmp"}
    text_suffixes = {".py", ".md", ".json", ".toml", ".yml", ".yaml"}

    for path in _walk_skip_dirs(PROJ):
        if not path.is_file() or path.resolve() == SELF_PATH:
            continue

        if path.suffix in forbidden_extensions:
            if interactive:
                if not interactive_artifact_resolver(path):
                    check_for_forbidden_artifacts(interactive)
                    return
                continue
            sys.exit("[halt] loose backup file found: " + str(path.relative_to(PROJ)) + " (rerun with --interactive)")

        if path.suffix in text_suffixes:
            try:
                lines = path.read_text(encoding="utf-8").splitlines()
            except (UnicodeDecodeError, OSError):
                continue
            has_conflict = any(
                line.startswith("<<<<<<< ") or line.rstrip() == "=======" or line.startswith(">>>>>>> ")
                for line in lines
            )
            if has_conflict:
                if interactive:
                    if not interactive_artifact_resolver(path):
                        check_for_forbidden_artifacts(interactive)
                        return
                    continue
                sys.exit("[halt] unresolved merge markers in: " + str(path.relative_to(PROJ)))

    print("[ok] no stray backups or merge markers found")


def check_credential_leaks():
    print("\n=== 2/9 credential leak scan (diff) ===")
    res = subprocess.run(["git", "diff", "--cached"], cwd=PROJ, capture_output=True, text=True)
    diff_text = res.stdout
    if not diff_text.strip():
        res = subprocess.run(["git", "diff"], cwd=PROJ, capture_output=True, text=True)
        diff_text = res.stdout

    pattern = re.compile(r"(?i)(password|secret|key|token|passwd)\s*=\s*['\"][A-Za-z0-9_\-]{8,}['\"]")
    if pattern.search(diff_text):
        sys.exit("[halt] potential hardcoded credential found in diff - remove before shipping")
    print("[ok] no obvious hardcoded credentials found")


def auto_format_lint():
    print("\n=== [optional] auto-format ===")
    if shutil.which("ruff"):
        print("[lint] running ruff format + check --fix")
        run(["ruff", "format", "."], check=False)
        run(["ruff", "check", ".", "--fix"], check=False)
    elif shutil.which("black"):
        print("[lint] running black")
        run(["black", "."], check=False)
    else:
        print("[skip] neither ruff nor black found on PATH")


def scan_technical_debt():
    print("\n=== 3/9 technical debt scan (informational) ===")
    r = subprocess.run(["git", "diff", "--name-only"], cwd=PROJ, capture_output=True, text=True)
    changed = [PROJ / f for f in r.stdout.splitlines() if f.endswith(".py")]
    markers = ["TODO:", "FIXME:", "BUG:"]
    found = 0
    for f in changed:
        if not f.is_file():
            continue
        for i, line in enumerate(f.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
            if any(m in line for m in markers):
                print("  -> " + str(f.relative_to(PROJ)) + ":" + str(i) + " -> " + line.strip())
                found += 1
    if not found:
        print("  [clean] no TODO/FIXME/BUG tags in changed files")


def preview_impacted_tests():
    print("\n=== 4/9 impacted-tests preview (informational only) ===")
    r = subprocess.run(["git", "diff", "--name-only"], cwd=PROJ, capture_output=True, text=True)
    changed_files = r.stdout.splitlines()
    targets = []
    for f in changed_files:
        if f.startswith("src/utils/") and f.endswith(".py"):
            module_name = Path(f).stem
            candidate = PROJ / "tests" / ("test_" + module_name + ".py")
            if candidate.exists():
                targets.append(str(candidate.relative_to(PROJ)))
    if targets:
        print("[info] likely-impacted test files: " + str(targets))
    else:
        print("[info] no direct src/utils/*.py changes detected")
    print("[info] full suite will still run as the actual gate below")


def run_tests():
    print("\n=== 5/9 pytest (with coverage) ===")
    r = run(
        [PY, "-m", "pytest", "-q", "--cov=src", "--cov-report=term-missing"],
        check=False,
        spinner_msg="Running test suite",
    )
    if r.returncode != 0:
        (PROJ / ".last_test_ok").unlink(missing_ok=True)
        sys.exit("[halt] tests failing - fix before shipping")
    print("[ok] all tests passed")
    return r.stdout


def enforce_coverage_floor(pytest_output: str):
    print("\n=== 6/9 coverage floor check ===")
    match = re.search(r"^TOTAL\s+\d+\s+\d+\s+(\d+)%", pytest_output, re.MULTILINE)
    if not match:
        print("[warn] could not parse coverage percentage, skipping floor check")
        return
    current = float(match.group(1))
    if COV_CACHE.exists():
        try:
            last = float(COV_CACHE.read_text().strip())
            if current < last:
                sys.exit("[halt] coverage dropped from " + str(last) + "% to " + str(current) + "% - fix before shipping")
            print("[ok] coverage maintained or improved: " + str(current) + "% (was " + str(last) + "%)")
        except ValueError:
            print("[warn] .last_cov_score was corrupt, resetting")
    COV_CACHE.write_text(str(current))


def predict_next_version(commit_message: str) -> str:
    hatch_py = PROJ / "hatch.py"
    current = "v0.0.0"
    if hatch_py.exists():
        m = re.search(r'VERSION\s*=\s*"([\d.]+)"', hatch_py.read_text())
        if m:
            current = "v" + m.group(1)

    try:
        major, minor, patch = map(int, current.lstrip("v").split("."))
    except ValueError:
        return current

    if "BREAKING CHANGE" in commit_message:
        major, minor, patch = major + 1, 0, 0
    elif commit_message.startswith("feat"):
        minor, patch = minor + 1, 0
    elif commit_message.startswith(("fix", "chore")):
        patch += 1

    return "v" + str(major) + "." + str(minor) + "." + str(patch)


def check_dirty():
    print("\n=== 7/9 git status ===")
    r = run(["git", "status", "--porcelain"])
    if not r.stdout.strip():
        sys.exit("[halt] nothing to commit - working tree clean")
    print(r.stdout)


def commit_and_push(message):
    print("\n=== 8/9 stage + commit + push ===")
    run(["git", "add", "-A"])
    run(["git", "commit", "-m", message])

    predicted = predict_next_version(message)
    print("[semver] next version would be: " + predicted + " (informational, not applied automatically)")

    new_head = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=PROJ, capture_output=True, text=True
    ).stdout.strip()
    (PROJ / ".last_test_ok").write_text(new_head)
    print("[marker] stamped .last_test_ok with " + new_head)

    if not is_online():
        print("[offline] network unavailable - commit is local, push deferred")
        print("[offline] run git push manually once you are back online")
        return

    r = run(["git", "push"], check=False)
    if r.returncode != 0:
        sys.exit("[halt] push failed - check auth/network, commit is local and safe")


def cleanup_pipeline_clutter():
    print("\n=== cleanup ===")
    clutter_dirs = {".pytest_cache", "htmlcov", "__pycache__", ".ipynb_checkpoints"}
    clutter_files = {".coverage"}

    for path in _walk_skip_dirs(PROJ):
        if path.is_dir() and path.name in clutter_dirs:
            shutil.rmtree(path, ignore_errors=True)
            print("[clean] removed dir: " + str(path.relative_to(PROJ)))
        elif path.is_file() and path.name in clutter_files:
            path.unlink(missing_ok=True)
            print("[clean] removed file: " + str(path.relative_to(PROJ)))


def track_pipeline_velocity(start_time: float):
    duration = time.time() - start_time
    if RUNTIME_CACHE.exists():
        try:
            prev = float(RUNTIME_CACHE.read_text().strip())
            delta = duration - prev
            if delta > 2.0:
                print("\n[perf][WARN] pipeline took " + "{:.2f}".format(duration) + "s (+" + "{:.2f}".format(delta) + "s slower than last run)")
            else:
                print("\n[perf][OK] execution stable at " + "{:.2f}".format(duration) + "s")
        except ValueError:
            pass
    RUNTIME_CACHE.write_text("{:.2f}".format(duration))


def print_ci_link():
    r = run(["git", "remote", "get-url", "origin"], check=False)
    url = r.stdout.strip()
    if url.endswith(".git"):
        url = url[:-4]
    if url.startswith("git@github.com:"):
        url = "https://github.com/" + url.split("git@github.com:")[1]
    print("\n[done] CI run (once pushed): " + url + "/actions")


def main():
    parser = argparse.ArgumentParser(description="Ship pipeline for stunning-octo-funicular")
    parser.add_argument("message", help="commit message")
    parser.add_argument("--interactive", action="store_true", help="prompt to resolve stray artifacts instead of halting")
    parser.add_argument("--format", action="store_true", help="run ruff/black auto-formatting before staging")
    args = parser.parse_args()

    start = time.time()

    verify_remote_sync()
    check_for_forbidden_artifacts(interactive=args.interactive)
    check_credential_leaks()
    if args.format:
        auto_format_lint()
    scan_technical_debt()
    preview_impacted_tests()
    pytest_output = run_tests()
    enforce_coverage_floor(pytest_output)
    check_dirty()
    commit_and_push(args.message)
    cleanup_pipeline_clutter()
    track_pipeline_velocity(start)
    print_ci_link()


if __name__ == "__main__":
    main()
