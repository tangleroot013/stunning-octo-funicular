#!/usr/bin/env python3
"""God Mode Scaffolder: create ready-to-use Python project templates with Git safety hooks."""

from __future__ import annotations

import argparse
import os
import re
import stat
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional

DEFAULT_CLAUDEIGNORE = [
    ".git",
    ".venv",
    "venv/",
    "__pycache__/",
    "*.pyc",
    "*.pyo",
    "*.pyd",
    "build/",
    "dist/",
    "*.egg-info/",
    ".idea/",
    ".vscode/",
    ".DS_Store",
    "node_modules/",
    "*.log",
]

SECRET_PATTERN = re.compile(r"(ANTHROPIC_API_KEY|github_token|password|secret|DATABASE_URL)", re.I)
TEMPLATE_CHOICES = ["cli", "web", "lib"]

COMMIT_MESSAGE_TEMPLATE = """# Conventional Commit Message Template
# format: type(scope): short description
# example: feat(api): add health-check route

feat(scope): description

# body
# - more details if needed
# - reference issue numbers as needed

# BREAKING CHANGE: describe any breaking change here
"""

PRE_COMMIT_HOOK = r"""#!/usr/bin/env python3
import os
import re
import subprocess
import sys
from pathlib import Path

SECRET_PATTERN = re.compile(r"(ANTHROPIC_API_KEY|github_token|password|secret|DATABASE_URL)", re.I)


def run_command(command, cwd=None):
    result = subprocess.run(command, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        print(result.stderr.strip(), file=sys.stderr)
    return result


def get_staged_files():
    result = run_command(["git", "diff", "--cached", "--name-only", "--diff-filter=ACMRTUXB"])
    if result.returncode != 0:
        sys.exit(1)
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def read_index_file(path):
    result = run_command(["git", "show", f":{path}"])
    if result.returncode != 0:
        return None
    return result.stdout.splitlines()


def check_secrets(staged_files):
    failures = []
    for path in staged_files:
        if not path.endswith(('.py', '.yml', '.yaml', '.json', '.md', '.env')):
            continue
        content = read_index_file(path)
        if content is None:
            continue
        for line_number, line in enumerate(content, start=1):
            if SECRET_PATTERN.search(line):
                failures.append(f"{path}:{line_number}: secret pattern detected")
    return failures


def check_python_syntax(staged_files):
    failures = []
    python_files = [path for path in staged_files if path.endswith('.py')]
    for path in python_files:
        result = run_command([sys.executable, "-m", "py_compile", path])
        if result.returncode != 0:
            failures.append(f"Python syntax error in staged file: {path}")
    return failures


def check_trailing_whitespace(staged_files):
    failures = []
    for path in staged_files:
        content = read_index_file(path)
        if content is None:
            continue
        for line_number, line in enumerate(content, start=1):
            if line.endswith(' ') or line.endswith('\t'):
                failures.append(f"{path}:{line_number}: trailing whitespace detected")
    return failures


def main():
    staged_files = get_staged_files()
    if not staged_files:
        sys.exit(0)

    failures = []
    failures.extend(check_secrets(staged_files))
    failures.extend(check_python_syntax(staged_files))
    failures.extend(check_trailing_whitespace(staged_files))

    if failures:
        print("QUACK! Pre-commit checks failed. Fix the following issues before committing:")
        for failure in failures:
            print(f"  - {failure}")
        sys.exit(1)

    sys.exit(0)


if __name__ == '__main__':
    main()
"""

PYTHON_APP_CI = """name: Python package

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.9, 3.11]
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          python -m pip install -r requirements.txt
      - name: Run tests
        run: pytest
"""


def make_executable(path: Path) -> None:
    mode = path.stat().st_mode
    path.chmod(mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def safe_write_text(path: Path, content: str, overwrite: bool = False) -> None:
    if path.exists() and not overwrite:
        return
    path.write_text(content, encoding="utf-8")


def make_directory(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def shell_run(command: List[str], cwd: Optional[Path] = None, capture_output: bool = False) -> subprocess.CompletedProcess:
    try:
        return subprocess.run(command, cwd=cwd, check=False, stdout=subprocess.PIPE if capture_output else None, stderr=subprocess.PIPE if capture_output else None, text=True)
    except FileNotFoundError:
        raise RuntimeError(f"Required command not found: {command[0]}") from None


def render_cli_template(root: Path) -> None:
    make_directory(root / "src")
    make_directory(root / "tests")
    make_directory(root / "docs")
    make_directory(root / "scripts")
    make_directory(root / ".github" / "workflows")

    safe_write_text(root / "src" / "main.py", """#!/usr/bin/env python3
import argparse
import logging


def main():
    parser = argparse.ArgumentParser(description="Command-line utility scaffolded by God Mode Scaffolder.")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    parser.add_argument("--input", help="Path to input file")
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)
    logging.info("God Mode CLI is ready")
    if args.input:
        logging.info(f"Processing input: {args.input}")


if __name__ == '__main__':
    main()
""")

    safe_write_text(root / "tests" / "test_main.py", """from src.main import main


def test_main_runs():
    # Basic sanity check for import and entrypoint.
    assert callable(main)
""")

    safe_write_text(root / "requirements.txt", """
# No additional runtime dependencies required for CLI template
""".strip() + "\n")
    safe_write_text(root / ".github" / "workflows" / "python-app.yml", PYTHON_APP_CI)


def render_web_template(root: Path) -> None:
    make_directory(root / "src" / "api")
    make_directory(root / "src" / "core")
    make_directory(root / "src" / "static")
    make_directory(root / "tests")
    make_directory(root / "docs")
    make_directory(root / "scripts")
    make_directory(root / ".github" / "workflows")

    safe_write_text(root / "src" / "main.py", """from fastapi import FastAPI
from api.router import router

app = FastAPI(title='God Mode Web Service')
app.include_router(router)
""")

    safe_write_text(root / "src" / "api" / "router.py", """from fastapi import APIRouter

router = APIRouter()


@router.get('/health')
def health_check():
    return {'status': 'ok', 'service': 'God Mode Web Service'}
""")

    safe_write_text(root / "tests" / "test_main.py", """from fastapi.testclient import TestClient
from src.main import app


def test_health_endpoint():
    client = TestClient(app)
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json() == {'status': 'ok', 'service': 'God Mode Web Service'}
""")

    safe_write_text(root / "requirements.txt", """fastapi>=0.100.0
uvicorn[standard]>=0.22.0
""")
    safe_write_text(root / ".github" / "workflows" / "python-app.yml", PYTHON_APP_CI)


def render_lib_template(root: Path) -> None:
    package_name = sanitize_package_name(root.name)
    make_directory(root / "src" / package_name)
    make_directory(root / "tests")
    make_directory(root / "docs")
    make_directory(root / "scripts")
    make_directory(root / ".github" / "workflows")

    safe_write_text(root / "src" / package_name / "__init__.py", f"""__version__ = '0.1.0'

__all__ = ['calculate']

from .core import calculate
""")

    safe_write_text(root / "src" / package_name / "core.py", """def calculate(value: int) -> int:
    \"\"\"Base library function placeholder. Returns the input multiplied by 2.\"\"\"
    return value * 2
""")

    safe_write_text(root / "tests" / "test_core.py", f"""from {package_name}.core import calculate


def test_calculate():
    assert calculate(2) == 4
""")

    safe_write_text(root / "requirements.txt", """setuptools>=68.0.0
wheel>=0.40.0
""")
    safe_write_text(root / ".github" / "workflows" / "python-app.yml", PYTHON_APP_CI)


def sanitize_package_name(name: str) -> str:
    return re.sub(r'[^a-zA-Z0-9_]', '_', name).strip('_').lower() or 'god_mode_package'


def create_project_readme(root: Path, template: str) -> None:
    lines = [
        f"# {root.name}",
        "",
        "Generated by God Mode Scaffolder.",
        "",
        "## Template",
        f"- {template}",
        "",
        "## Getting started",
        "",
        "```bash",
        "python3 -m pip install -r requirements.txt",
        "pytest",
        "```",
        "",
        "## Git safety",
        "",
        "This scaffold includes a local Git pre-commit hook and commit template for cleaner history.",
    ]
    safe_write_text(root / "README.md", "\n".join(lines) + "\n")


def create_claudeignore(root: Path) -> None:
    path = root / ".claudeignore"
    safe_write_text(path, "\n".join(DEFAULT_CLAUDEIGNORE) + "\n")


def create_gitignore(root: Path) -> None:
    patterns = [
        "__pycache__/",
        "*.py[cod]",
        ".venv/",
        "build/",
        "dist/",
        "*.egg-info/",
    ]
    path = root / ".gitignore"
    if path.exists():
        existing = path.read_text(encoding="utf-8").splitlines()
        merged = existing[:]
        for pattern in patterns:
            if pattern not in merged:
                merged.append(pattern)
        path.write_text("\n".join(merged).rstrip() + "\n", encoding="utf-8")
        return
    safe_write_text(path, "\n".join(patterns) + "\n")


def init_git_repository(root: Path) -> None:
    if (root / ".git").exists():
        return
    try:
        shell_run(["git", "init"], cwd=root)
    except RuntimeError as exc:
        print(f"Warning: git not available ({exc}). Skipping repository initialization.")


def write_pre_commit_hook(root: Path) -> None:
    hooks_dir = root / ".git" / "hooks"
    make_directory(hooks_dir)
    script_path = hooks_dir / "pre-commit"
    safe_write_text(script_path, PRE_COMMIT_HOOK)
    make_executable(script_path)


def write_commit_template(root: Path) -> None:
    safe_write_text(root / ".gitmessage", COMMIT_MESSAGE_TEMPLATE)
    if (root / ".git").exists():
        try:
            shell_run(["git", "config", "commit.template", str(root / ".gitmessage")], cwd=root)
        except RuntimeError:
            pass


def setup_global_git_templates() -> None:
    home = Path.home()
    template_dir = home / ".git-templates"
    hooks_dir = template_dir / "hooks"
    make_directory(hooks_dir)
    safe_write_text(hooks_dir / "pre-commit", PRE_COMMIT_HOOK)
    make_executable(hooks_dir / "pre-commit")
    safe_write_text(home / ".gitmessage", COMMIT_MESSAGE_TEMPLATE)
    try:
        shell_run(["git", "config", "--global", "init.templateDir", str(template_dir)])
        shell_run(["git", "config", "--global", "commit.template", str(home / ".gitmessage")])
    except RuntimeError as exc:
        raise SystemExit(f"Failed to configure global Git templates: {exc}")


def resolve_target_root(project_name: Optional[str], base_path: Optional[str]) -> Path:
    base = Path(base_path).expanduser().resolve() if base_path else Path.cwd().resolve()
    if project_name:
        return base / project_name
    return base


def ensure_directory_safe(root: Path) -> None:
    if root.exists() and any(root.iterdir()):
        raise SystemExit(f"Target directory already exists and is not empty: {root}")
    root.mkdir(parents=True, exist_ok=True)


def bootstrap_project(root: Path, template: str) -> None:
    ensure_directory_safe(root)
    create_claudeignore(root)
    create_gitignore(root)
    create_project_readme(root, template)

    if template == "cli":
        render_cli_template(root)
    elif template == "web":
        render_web_template(root)
    else:
        render_lib_template(root)

    init_git_repository(root)
    write_pre_commit_hook(root)
    write_commit_template(root)

    print(f"Created {template} project scaffold at: {root}")
    print("Run `cd {root}` then install requirements and start your new project.")


def describe_environment() -> str:
    python = sys.executable
    return f"Python {sys.version.split()[0]} using interpreter {python}"


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="hatch",
        description="Generate production-ready Python scaffolds and Git safety templates.",
    )
    parser.add_argument("project_name", nargs="?", help="Optional name of the generated project directory.")
    parser.add_argument("base_path", nargs="?", help="Optional parent directory for project generation.")
    parser.add_argument(
        "-t",
        "--template",
        choices=TEMPLATE_CHOICES,
        default="cli",
        help="Project scaffold template to generate.",
    )
    parser.add_argument(
        "--setup-global",
        action="store_true",
        help="Configure a global Git template directory for future repository initialization.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_arguments()
    if args.setup_global:
        setup_global_git_templates()
        print("Global Git templates configured at ~/.git-templates and ~/.gitmessage")

    if args.project_name or not args.setup_global:
        target_root = resolve_target_root(args.project_name, args.base_path)
        bootstrap_project(target_root, args.template)
        print(f"Bootstrapped project with template '{args.template}'.")

    print(describe_environment())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
