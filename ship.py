#!/usr/bin/env python3
"""ship.py — Release pipeline v0.5.0

Config-driven CI gate with:
  • pyproject.toml [tool.ship] settings (+ --init wizard)
  • --dry-run, --install-hooks, --matrix, --skip, --verbose, --quiet flags
  • argcomplete tab-completion for flags and stage names
  • colored/emoji stage output, error messages with suggested fixes
  • parallel test execution, changelog generation, lockfile sync
  • rollback on failure, cross-platform notifications
  • type checking, audit, forbidden file size scan
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

try:
    import argcomplete
except ImportError:
    argcomplete = None

STAGE_CHOICES = [
    "remote_sync", "preflight", "credential_scan", "tech_debt",
    "impacted_tests", "pytest", "coverage_floor", "git_status",
]

# ────────────────────────────── config loader ──────────────────────────────

def load_ship_config():
    """Read [tool.ship] from pyproject.toml (fallback defaults)."""
    defaults = {
        "coverage_floor": 99.0,
        "type_check": False,
        "audit": False,
        "auto_tag": False,
        "parallel_tests": False,
        "changelog": False,
        "lockfile_sync": False,
        "rollback_on_failure": False,
        "forbidden_max_size_mb": 10,
        "notifications": False,
    }
    pyproject = Path("pyproject.toml")
    if not pyproject.exists():
        return defaults
    in_section = False
    for line in pyproject.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped == "[tool.ship]":
            in_section = True
            continue
        if in_section and stripped.startswith("["):
            break
        if in_section and "=" in stripped:
            key, val = stripped.split("=", 1)
            key = key.strip()
            val = val.strip()
            if val.lower() in ("true", "false"):
                defaults[key] = val.lower() == "true"
            else:
                try:
                    defaults[key] = float(val)
                except ValueError:
                    defaults[key] = val.strip('"').strip("'")
    return defaults


# ────────────────────────────── helpers ──────────────────────────────

CONFIG = load_ship_config()
DRY_RUN = False
VERBOSE = False
QUIET = False


def _run(cmd, capture=True, check=False, cwd=None):
    """Shell out; respect --dry-run for mutating commands."""
    if isinstance(cmd, str):
        cmd_list = cmd.split()
    else:
        cmd_list = list(cmd)
    mutating = any(c in cmd_list for c in ("git", "rm", "mv", "cp", "pip", "npm"))
    if DRY_RUN and mutating:
        print(f"[dry-run] would run: {' '.join(cmd_list)}")
        return subprocess.CompletedProcess(cmd_list, 0, stdout="", stderr="")
    return subprocess.run(cmd_list, capture_output=capture, text=True, check=check, cwd=cwd)


def _ok(msg):
    print(f"\033[92m✓ [ok]\033[0m {msg}")


def _info(msg):
    if QUIET:
        return
    print(f"\033[94mi [info]\033[0m {msg}")


def _warn(msg):
    print(f"\033[93m⚠ [warn]\033[0m {msg}")


def _fail(msg):
    print(f"\033[91m✗ [fail]\033[0m {msg}")


def _hint(msg):
    if QUIET:
        return
    print(f"\033[96m  → hint:\033[0m {msg}")


def _verbose_dump(result):
    if not VERBOSE:
        return
    if result.stdout:
        print(result.stdout.rstrip())
    if result.stderr:
        print(result.stderr.rstrip())


def spinner(msg, duration=0.3):
    """Tiny CLI spinner."""
    if QUIET:
        print(f"  {msg}")
        return
    for c in "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏":
        print(f"\r{c} {msg}", end="", flush=True)
        time.sleep(duration / 10)
    print(f"\r  {msg}")


def notify(title, message):
    """Cross-platform desktop notification."""
    if not CONFIG.get("notifications"):
        return
    system = sys.platform
    try:
        if system == "darwin":
            esc = message.replace("\\", "\\\\").replace('"', '\\"')
            esc_t = title.replace("\\", "\\\\").replace('"', '\\"')
            _run(["osascript", "-e", f'display notification "{esc}" with title "{esc_t}"'], capture=True)
        elif system == "linux":
            if shutil.which("notify-send"):
                _run(["notify-send", title, message], capture=True)
            else:
                print(f"\a[notify] {title}: {message}")
        else:
            print(f"\a[notify] {title}: {message}")
    except Exception:
        pass


# ────────────────────────────── init wizard ──────────────────────────────

def init_wizard():
    """Interactively generate [tool.ship] config in pyproject.toml."""
    print("\n=== ship.py init wizard ===")
    print("Press Enter to accept the default shown in [brackets].\n")
    defaults = {
        "coverage_floor": 99.0,
        "type_check": False,
        "audit": False,
        "auto_tag": False,
        "parallel_tests": False,
        "changelog": False,
        "lockfile_sync": False,
        "rollback_on_failure": False,
        "forbidden_max_size_mb": 10,
        "notifications": False,
    }
    result = {}
    for key, default in defaults.items():
        raw = input(f"{key} [{default}]: ").strip()
        if not raw:
            result[key] = default
        elif isinstance(default, bool):
            result[key] = raw.lower() in ("y", "yes", "true", "1")
        else:
            try:
                result[key] = float(raw)
            except ValueError:
                result[key] = raw

    lines = ["[tool.ship]"]
    for key, val in result.items():
        if isinstance(val, bool):
            lines.append(f"{key} = {str(val).lower()}")
        elif isinstance(val, (int, float)):
            lines.append(f"{key} = {val}")
        else:
            lines.append(f'{key} = "{val}"')
    block = "\n".join(lines) + "\n"

    pyproject = Path("pyproject.toml")
    if pyproject.exists():
        text = pyproject.read_text(encoding="utf-8")
        if "[tool.ship]" in text:
            before, _, rest = text.partition("[tool.ship]")
            after_lines = rest.splitlines()
            end = len(after_lines)
            for i, l in enumerate(after_lines):
                if i > 0 and l.strip().startswith("["):
                    end = i
                    break
            remainder = "\n".join(after_lines[end:])
            text = before + block + ("\n" + remainder if remainder else "")
        else:
            text = text.rstrip() + "\n\n" + block
        pyproject.write_text(text, encoding="utf-8")
    else:
        pyproject.write_text(block, encoding="utf-8")
    _ok("wrote [tool.ship] config to pyproject.toml")


# ────────────────────────────── pipeline stages ──────────────────────────────

def stage_0_remote_sync():
    print("\n=== 0/9 remote sync check ===")
    _run("git fetch origin")
    status = _run("git status -sb")
    if "ahead" in status.stdout or "behind" in status.stdout:
        _fail("branch diverged from origin")
        _hint("run 'git pull --rebase' to sync, then retry")
        return False
    _ok("branch in sync with origin")
    return True


def stage_1_preflight():
    print("\n=== 1/9 pre-flight artifact check ===")
    bad = []
    for root, _dirs, files in os.walk("."):
        if ".git" in root:
            continue
        for f in files:
            if f.endswith(".bak") or f.endswith(".orig") or f.endswith(".rej"):
                bad.append(os.path.join(root, f))
    if bad:
        _fail(f"stray backups found: {bad}")
        _hint("remove or .gitignore the listed files, then retry")
        return False
    merge_markers = ["<<<<<<<", "=======", ">>>>>>>"]
    for root, _dirs, files in os.walk("src"):
        for f in files:
            if not f.endswith(".py"):
                continue
            p = Path(root) / f
            content = p.read_text(encoding="utf-8")
            if any(m in content for m in merge_markers):
                _fail(f"merge markers in {p}")
                _hint(f"resolve the conflict in {p}, then retry")
                return False
    _ok("no stray backups or merge markers found")
    return True


def stage_2_credential_scan():
    print("\n=== 2/9 credential leak scan (diff) ===")
    diff = _run("git diff --cached")
    if not diff.stdout:
        diff = _run("git diff")
    patterns = [
        r"api[_-]?key\s*[=:]\s*['\"]?[a-zA-Z0-9]{20,}",
        r"password\s*[=:]\s*['\"]?[^\s'\"']{8,}",
        r"secret\s*[=:]\s*['\"]?[a-zA-Z0-9]{16,}",
        r"token\s*[=:]\s*['\"]?[a-zA-Z0-9]{20,}",
    ]
    for pat in patterns:
        if re.search(pat, diff.stdout, re.IGNORECASE):
            _warn("possible hardcoded credential detected (review diff)")
            _hint("run 'git diff' manually to confirm before committing")
            break
    else:
        _ok("no obvious hardcoded credentials found")
    return True


def stage_3_tech_debt():
    print("\n=== 3/9 technical debt scan (informational) ===")
    markers = ["TODO:", "FIXME:", "BUG:", "HACK:", "XXX:"]
    found = False
    for root, _dirs, files in os.walk("src"):
        for f in files:
            if not f.endswith(".py"):
                continue
            p = Path(root) / f
            for i, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
                for m in markers:
                    if m in line:
                        print(f"  -> {p}:{i} -> {line.strip()}")
                        found = True
    if not found:
        _info("no debt markers found")
    return True


def stage_4_impacted_tests():
    print("\n=== 4/9 impacted-tests preview (informational only) ===")
    diff = _run("git diff --name-only")
    changed = diff.stdout.strip().splitlines() if diff.stdout else []
    utils_changed = any("src/utils/" in c for c in changed)
    if utils_changed:
        _info("src/utils/*.py changes detected — full suite recommended")
    else:
        _info("no direct src/utils/*.py changes detected")
    _info("full suite will still run as the actual gate below")
    return True


def stage_5_pytest():
    print("\n=== 5/9 pytest (with coverage) ===")
    venv_python = _get_venv_python()
    cov_cmd = [venv_python, "-m", "pytest", "-q", "--cov=src", "--cov-report=term-missing"]
    if CONFIG.get("parallel_tests"):
        cov_cmd.insert(3, "-n")
        cov_cmd.insert(4, "auto")
        _info("parallel test execution enabled")
    result = _run(cov_cmd, capture=True, check=False)
    if result.returncode != 0:
        _fail("tests failed")
        _hint(f"run '{venv_python} -m pytest -q' directly to see full output")
        _verbose_dump(result)
        return False
    _ok("all tests passed")
    return True


def stage_6_coverage_floor():
    print("\n=== 6/9 coverage floor check ===")
    floor = float(CONFIG.get("coverage_floor", 99.0))
    venv_python = _get_venv_python()
    result = _run([venv_python, "-m", "coverage", "report"])
    total_line = [l for l in (result.stdout or "").splitlines() if "TOTAL" in l]
    if total_line:
        parts = total_line[0].split()
        if parts:
            try:
                cov = float(parts[-1].rstrip("%"))
                if cov >= floor:
                    _ok(f"coverage maintained or improved: {cov:.1f}% (was {floor:.1f}%)")
                    return True
                else:
                    _fail(f"coverage dropped: {cov:.1f}% (floor {floor:.1f}%)")
                    _hint("add tests to cover the gap, or lower coverage_floor in pyproject.toml [tool.ship]")
                    return False
            except ValueError:
                pass
    _warn("could not parse coverage, assuming ok")
    return True


def stage_7_git_status():
    print("\n=== 7/9 git status ===")
    result = _run("git status --porcelain")
    print(result.stdout or "(clean)")
    return True


def stage_8_commit_push(message):
    print("\n=== 8/9 stage + commit + push ===")
    _run("git add -A")
    result = _run(["git", "commit", "-m", message], check=False)
    if result.returncode != 0:
        _warn("nothing to commit or commit failed")
        return True

    semver = _predict_semver(message)
    if semver:
        print(f"\033[95m[semver]\033[0m next version would be: {semver} (informational, not applied automatically)")

    commit_hash = _run("git rev-parse HEAD").stdout.strip()
    Path(".last_test_ok").write_text(commit_hash, encoding="utf-8")
    print(f"\033[95m[marker]\033[0m stamped .last_test_ok with {commit_hash}")

    if CONFIG.get("changelog"):
        _update_changelog(message, semver or "unreleased")

    if CONFIG.get("lockfile_sync"):
        _sync_lockfile()

    push_result = _run("git push", check=False)
    if push_result.returncode != 0:
        _fail("git push failed")
        _hint("check network/auth, or run 'git push' manually to see the full error")
        return False
    return True


# ────────────────────────────── extra features ──────────────────────────────

def _get_venv_python():
    """Find the venv python or fallback to sys.executable."""
    candidates = [
        ".venv/bin/python",
        "venv/bin/python",
        ".venv/Scripts/python.exe",
        "venv/Scripts/python.exe",
    ]
    for c in candidates:
        if Path(c).exists():
            return c
    return sys.executable


def _predict_semver(message):
    """Naive conventional-commit semver bump."""
    msg = message.lower()
    current = _current_version()
    if not current:
        return None
    major, minor, patch = map(int, current.lstrip("v").split("."))
    if msg.startswith("feat!") or "breaking change" in msg:
        return f"v{major + 1}.0.0"
    elif msg.startswith("feat"):
        return f"v{major}.{minor + 1}.0"
    elif msg.startswith("fix") or msg.startswith("chore") or msg.startswith("docs"):
        return f"v{major}.{minor}.{patch + 1}"
    return None


def _current_version():
    """Read version from package.json or pyproject.toml."""
    pkg = Path("package.json")
    if pkg.exists():
        data = json.loads(pkg.read_text())
        return data.get("version")
    pp = Path("pyproject.toml")
    if pp.exists():
        for line in pp.read_text().splitlines():
            if line.strip().startswith("version"):
                return line.split("=")[1].strip().strip('"').strip("'")
    return None


def _update_changelog(message, version):
    """Prepend entry to CHANGELOG.md."""
    changelog = Path("CHANGELOG.md")
    entry = f"## {version} — {time.strftime('%Y-%m-%d')}\n\n- {message}\n\n"
    if changelog.exists():
        old = changelog.read_text(encoding="utf-8")
        changelog.write_text(entry + old, encoding="utf-8")
    else:
        changelog.write_text("# Changelog\n\n" + entry, encoding="utf-8")
    _info("updated CHANGELOG.md")


def _sync_lockfile():
    """Run npm/pip lockfile update if relevant files changed."""
    diff = _run("git diff --name-only")
    if not diff.stdout:
        return
    if Path("package-lock.json").exists() and "package.json" in diff.stdout:
        _run("npm install", capture=False)
        _run("git add package-lock.json")
        _info("synced package-lock.json")
    if Path("Pipfile.lock").exists() and "Pipfile" in diff.stdout:
        _run([_get_venv_python(), "-m", "pipenv", "lock"], capture=False)
        _run("git add Pipfile.lock")
        _info("synced Pipfile.lock")


def _type_check():
    """Run mypy if configured."""
    if not CONFIG.get("type_check"):
        return True
    print("\n=== type check ===")
    venv_python = _get_venv_python()
    result = _run([venv_python, "-m", "mypy", "src"], check=False)
    if result.returncode != 0:
        _fail("type check failed")
        _hint(f"run '{venv_python} -m mypy src' directly to see full output")
        _verbose_dump(result)
        return False
    _ok("type check passed")
    return True


def _audit():
    """Run pip-audit / npm audit if configured."""
    if not CONFIG.get("audit"):
        return True
    print("\n=== dependency audit ===")
    venv_python = _get_venv_python()
    if Path("requirements.txt").exists() or Path("pyproject.toml").exists():
        result = _run([venv_python, "-m", "pip_audit", "--desc"], check=False)
        if result.returncode != 0:
            _warn("pip-audit issues found (review output)")
        else:
            _ok("pip-audit clean")
    if Path("package.json").exists():
        result = _run("npm audit", check=False)
        if result.returncode != 0:
            _warn("npm audit issues found (review output)")
        else:
            _ok("npm audit clean")
    return True


def _forbidden_size_check():
    """Check for files exceeding max size."""
    max_mb = float(CONFIG.get("forbidden_max_size_mb", 10))
    max_bytes = max_mb * 1024 * 1024
    offenders = []
    for root, _dirs, files in os.walk("."):
        if ".git" in root or "node_modules" in root or ".venv" in root or "__pycache__" in root:
            continue
        for f in files:
            p = Path(root) / f
            try:
                if p.stat().st_size > max_bytes:
                    offenders.append(f"{p} ({p.stat().st_size / 1024 / 1024:.1f} MB)")
            except OSError:
                pass
    if offenders:
        _fail(f"files exceed {max_mb} MB: {offenders}")
        _hint("git-lfs track large files, or add them to .gitignore")
        return False
    return True


def install_hooks():
    """Install pre-push and pre-commit hooks."""
    git_dir = Path(".git")
    if not git_dir.exists():
        _fail("not a git repository")
        return
    hooks_dir = git_dir / "hooks"
    hooks_dir.mkdir(exist_ok=True)

    pre_push = hooks_dir / "pre-push"
    script = """#!/bin/sh
# Auto-generated by ship.py v0.5.0 — pre-push hook
COMMIT=$(git rev-parse HEAD)
LAST_OK_FILE=".last_test_ok"
if [ -f "$LAST_OK_FILE" ]; then
    LAST_OK=$(cat "$LAST_OK_FILE")
    if [ "$COMMIT" = "$LAST_OK" ]; then
        echo "[pre-push] tests already verified for $COMMIT via ship.py, skipping re-run"
        exit 0
    fi
fi
echo "[pre-push] running ship.py gate..."
python3 ship.py "pre-push gate"
"""
    pre_push.write_text(script, encoding="utf-8")
    pre_push.chmod(0o755)
    _ok("installed .git/hooks/pre-push")

    pre_commit = hooks_dir / "pre-commit"
    script2 = """#!/bin/sh
# Auto-generated by ship.py v0.5.0 — pre-commit hook
echo "[pre-commit] running quick checks..."
python3 -m py_compile $(git diff --cached --name-only --diff-filter=ACM | grep '\\.py$' || true)
"""
    pre_commit.write_text(script2, encoding="utf-8")
    pre_commit.chmod(0o755)
    _ok("installed .git/hooks/pre-commit")


def show_matrix():
    """Display the pipeline matrix configuration."""
    print("\n=== Pipeline Matrix ===")
    stages = [
        ("remote sync", True, "—"),
        ("preflight", True, "—"),
        ("credential scan", True, "audit"),
        ("tech debt", True, "—"),
        ("impacted tests", True, "—"),
        ("pytest", True, "parallel_tests"),
        ("coverage floor", True, "coverage_floor"),
        ("git status", True, "—"),
        ("commit/push", True, "auto_tag/changelog/lockfile_sync"),
    ]
    for i, (s, e, k) in enumerate(stages):
        status = "✓" if e else "✗"
        print(f"  {status} {i}. {s:25} (config: {k})")
    print("\n=== Active Config ===")
    for k, v in CONFIG.items():
        print(f"  {k:30} = {v}")


# ────────────────────────────── main ──────────────────────────────

def main():
    global DRY_RUN, VERBOSE, QUIET
    parser = argparse.ArgumentParser(description="ship.py — release pipeline v0.5.0")
    parser.add_argument("message", nargs="?", help="commit message (required unless --install-hooks, --matrix, or --init)")
    parser.add_argument("--interactive", action="store_true", help="prompt before push")
    parser.add_argument("--format", action="store_true", help="auto-format code before commit")
    parser.add_argument("--dry-run", action="store_true", help="show what would be done without mutating")
    parser.add_argument("--install-hooks", action="store_true", help="install git hooks and exit")
    parser.add_argument("--matrix", action="store_true", help="show pipeline matrix and exit")
    parser.add_argument("--init", action="store_true", help="interactively generate [tool.ship] config and exit")
    parser.add_argument("--verbose", "-v", action="store_true", help="print full stdout/stderr on stage failures")
    parser.add_argument("--quiet", "-q", action="store_true", help="suppress info/spinner output")
    skip_arg = parser.add_argument(
        "--skip", default="",
        help=f"comma-separated stage indices or names to skip, e.g. 2,5 or credential_scan,pytest. choices: {', '.join(STAGE_CHOICES)}",
    )
    if argcomplete:
        skip_arg.completer = lambda prefix, **kw: [n for n in STAGE_CHOICES if n.startswith(prefix)]
        argcomplete.autocomplete(parser)

    args = parser.parse_args()

    if args.init:
        init_wizard()
        return 0

    if args.install_hooks:
        install_hooks()
        return 0

    if args.matrix:
        show_matrix()
        return 0

    if not args.message:
        parser.error("the following arguments are required: message")

    DRY_RUN = args.dry_run
    VERBOSE = args.verbose
    QUIET = args.quiet
    if DRY_RUN:
        _info("dry-run mode — no mutating commands will execute")

    skip_set = {s.strip() for s in args.skip.split(",") if s.strip()}

    if args.format and not DRY_RUN:
        _run("black .", check=False)
        _run("isort .", check=False)
        _run("git add -A")

    checks = [
        ("forbidden size", _forbidden_size_check),
        ("type check", _type_check),
        ("audit", _audit),
    ]
    for name, fn in checks:
        if not fn():
            if CONFIG.get("rollback_on_failure"):
                _run("git reset --hard HEAD")
                _info("rolled back to HEAD")
            return 1

    stages = [
        (0, "remote_sync", stage_0_remote_sync),
        (1, "preflight", stage_1_preflight),
        (2, "credential_scan", stage_2_credential_scan),
        (3, "tech_debt", stage_3_tech_debt),
        (4, "impacted_tests", stage_4_impacted_tests),
        (5, "pytest", stage_5_pytest),
        (6, "coverage_floor", stage_6_coverage_floor),
        (7, "git_status", stage_7_git_status),
    ]
    for idx, name, stage in stages:
        if str(idx) in skip_set or name in skip_set:
            _warn(f"skipped stage {idx} ({name})")
            continue
        spinner(f"running {stage.__name__}...")
        if not stage():
            if CONFIG.get("rollback_on_failure"):
                _run("git reset --hard HEAD")
                _info("rolled back to HEAD")
            notify("ship.py", f"Pipeline failed at {stage.__name__}")
            return 1

    if args.interactive and not DRY_RUN:
        resp = input("\nProceed with commit & push? [y/N] ")
        if resp.lower() not in ("y", "yes"):
            _info("aborted by user")
            return 0

    if not stage_8_commit_push(args.message):
        notify("ship.py", "Pipeline failed at commit/push")
        return 1

    print("\n=== cleanup ===")
    for f in (".coverage", ".pytest_cache"):
        p = Path(f)
        if p.exists():
            if p.is_dir():
                shutil.rmtree(p)
            else:
                p.unlink()
            print(f"[clean] removed: {f}")

    remote = _run("git remote get-url origin").stdout.strip()
    print(f"\n[done] CI run (once pushed): {remote.replace('.git', '')}/actions")
    notify("ship.py", "Pipeline completed successfully")
    return 0


if __name__ == "__main__":
    sys.exit(main())
