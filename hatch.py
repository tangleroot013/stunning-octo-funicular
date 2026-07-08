#!/usr/bin/env python3
"""
God Mode Scaffolder (hatch.py) – v0.2.2 “Waddler OS Pro”

Creates production-ready Python projects with:
  • Cross-platform pure-Python implementation
  • Automatic .claudeignore for token efficiency
  • Global/local Git pre-commit hooks (secret detection, syntax checks, Ruff, Black, isort, whitespace)
  • Expanded multi-stage CI/CD skeletons
  • Template-specific boilerplate (CLI, FastAPI, Library)

Author: Carter the Duck Developer 🦆
"""

import os
import sys
import json
import argparse
import subprocess
from pathlib import Path
from datetime import datetime, timezone

from src.utils.config_loader import settings

# ----------------------------------------------------------------------
# Constants (derived from the JSON spec)
# ----------------------------------------------------------------------
TEMPLATES = {
    "cli": {
        "dirs": ["src", "tests", "docs", "scripts", ".github/workflows"],
        "files": {
            "src/main.py": """#!/usr/bin/env python3
\"\"\"CLI entry point\"\"\"
import argparse

def main():
    parser = argparse.ArgumentParser(description='Your CLI tool')
    parser.add_argument('-v', '--version', action='store_true', help='Show version')
    args = parser.parse_args()
    if args.version:
        print('Version: {version}')
    else:
        print('Hello from {project_name}!')

if __name__ == '__main__':
    main()
""",
            "tests/test_main.py": """import subprocess, sys, pathlib

def test_cli_help():
    result = subprocess.run([sys.executable, 'src/main.py', '--help'],
                            capture_output=True, text=True)
    assert result.returncode == 0
    assert 'CLI entry point' in result.stdout
"""
        },
        "extra_deps": [
            "black>=23.0.0",
            "ruff>=0.1.0",
            "isort>=5.12.0",
            "pytest-cov>=4.1.0"
        ]
    },

    "web": {
        "dirs": [
            "src", "src/api", "src/core", "src/static",
            "tests", "docs", "scripts", ".github/workflows"
        ],
        "files": {
            "src/main.py": """#!/usr/bin/env python3
\"\"\"FastAPI application bootstrap\"\"\"
from fastapi import FastAPI
from src.api import router as api_router
from src.core.config import settings

app = FastAPI(title=settings.APP_NAME)

app.include_router(api_router)
""",
            "src/api/router.py": """from fastapi import APIRouter

router = APIRouter()

@router.get('/health')
def health_check():
    return {'status': 'ok'}
""",
            "src/core/config.py": """from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = 'WaddlerAPI'


settings = Settings()
""",
            "tests/test_main.py": """import json
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_health():
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json() == {'status': 'ok'}
"""
        },
        "extra_deps": [
            "fastapi>=0.100.0",
            "uvicorn[standard]>=0.22.0",
            "pydantic>=2.0.0",
            "pydantic-settings>=2.0.0",
            "black>=23.0.0",
            "ruff>=0.1.0",
            "isort>=5.12.0",
            "pytest-cov>=4.1.0"
        ]
    },

    "lib": {
        "dirs": ["src", "src/{package_name}", "tests", "docs", "scripts", ".github/workflows"],
        "files": {
            "src/{package_name}/__init__.py": """\"\"\"{project_name} package – version {version}\"\"\"
__all__ = ['core']
""",
            "src/{package_name}/core.py": """def validate_swim_distance(distance: float):
    \"\"\"Validate that a duck can safely swim a distance.\"\"\"
    if distance < 0:
        raise ValueError('Ducks cannot swim backwards!')
    return True
""",
            "tests/test_core.py": """import pytest
from src.{package_name}.core import validate_swim_distance


def test_validate_swim_distance():
    assert validate_swim_distance(3.5) is True


def test_validate_swim_distance_rejects_negative_values():
    with pytest.raises(ValueError):
        validate_swim_distance(-1)
"""
        },
        "extra_deps": [
            "setuptools>=68.0.0",
            "wheel>=0.40.0",
            "black>=23.0.0",
            "ruff>=0.1.0",
            "isort>=5.12.0",
            "pytest-cov>=4.1.0"
        ]
    },

    "default": {
        "dirs": ["src", "tests", "docs", ".github/workflows"],
        "files": {},
        "extra_deps": []
    }
}

CLAUDEIGNORE = """node_modules/
venv/
.venv/
__pycache__/
.git/
.vscode/
.idea/
.DS_Store
dist/
build/
*.exe
*.out
*.csv
*.jsonl
*.sql
.pytest_cache/
.coverage
htmlcov/
*.egg-info/
"""

GITIGNORE = """venv/
.venv/
__pycache__/
*.pyc
.pytest_cache/
.coverage
htmlcov/
*.egg-info/
.env
.DS_Store
dist/
build/
"""

PRE_COMMIT_HOOK_TEMPLATE = """#!/usr/bin/env bash
# -------------------------------------------------
# Pre-commit hook – secret detection, syntax checks,
# Ruff/Black/isort validation, and whitespace guard.
# -------------------------------------------------

set -e

# 1️⃣ Secret detection (CRITICAL)
if git diff --cached --name-only | grep -E '\\.py$|\\.env$|\\.yml$|\\.yaml$' | xargs grep -E -n '(ANTHROPIC_API_KEY|github_token|password|secret|DATABASE_URL)'; then
  echo "QUACK! Secret detected in staged changes!"
  exit 1
fi

# 2️⃣ Python syntax validation (HIGH)
python_files=$(git diff --cached --name-only --diff-filter=ACMR | grep '\\.py$' || true)
if [ -n "$python_files" ]; then
  python3 -m py_compile $python_files
fi

# 3️⃣ Quality checks (MEDIUM/HIGH)
if [ -n "$python_files" ]; then
  {hooks}
fi

# 4️⃣ Trailing whitespace (WARNING)
if git diff --cached --check | grep -q 'trailing whitespace'; then
  echo "Trailing whitespace detected!"
  exit 1
fi

exit 0
"""

GITMESSAGE = """# Conventional Commit Message
# ---------------------------
# <type>(<scope>): <subject>
# <BLANK LINE>
# <body>
# <BLANK LINE>
# <footer>
#
# Types: feat, fix, docs, style, refactor, perf, test, chore, ci
"""

WORKFLOW_YAML_TEMPLATE = """name: CI
on: [push, pull_request]
jobs:
  lint-and-format:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
      - name: Ruff check
        run: ruff check --fix .
      - name: Black check
        run: black --check .
      - name: Isort check
        run: isort --check-only .

  test:
    runs-on: ubuntu-latest
    needs: lint-and-format
    strategy:
      matrix:
        python-version: ['3.9', '3.10', '3.11', '3.12']
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
      - name: Install deps
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
      - name: Run tests
        run: |
          pytest --cov .
"""

# ----------------------------------------------------------------------
# Helper functions
# ----------------------------------------------------------------------
def render_template(content, **ctx):
    """Simple {{placeholder}} replacement"""
    for k, v in ctx.items():
        content = content.replace(f'{{{k}}}', v)
    return content


def write_file(path: Path, content: str, mode: str = "w"):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    if mode == "x":
        path.chmod(0o755)


def create_git_hook(project_path: Path, global_template: bool = False):
    hook_dir = (project_path / ".git" / "hooks") if not global_template else Path.home() / ".git-templates" / "hooks"
    hook_dir.mkdir(parents=True, exist_ok=True)
    hook_path = hook_dir / "pre-commit"
    hooks = settings.get("ci.pre_commit.hooks", [])
    hook_commands = []
    for hook in hooks:
        if hook == "detect-secrets":
            hook_commands.append('  if git diff --cached --name-only | grep -E \'\\.py$|\\.env$|\\.yml$|\\.yaml$\' | xargs grep -E -n \'(ANTHROPIC_API_KEY|github_token|password|secret|DATABASE_URL)\'; then')
            hook_commands.append('    echo "QUACK! Secret detected in staged changes!"')
            hook_commands.append('    exit 1')
            hook_commands.append('  fi')
        elif hook == "py_compile":
            hook_commands.append('  python_files=$(git diff --cached --name-only --diff-filter=ACMR | grep \'\\.py$\' || true)')
            hook_commands.append('  if [ -n "$python_files" ]; then')
            hook_commands.append('    python3 -m py_compile $python_files')
            hook_commands.append('  fi')
        elif hook == "ruff":
            hook_commands.append('  if [ -n "$python_files" ]; then')
            hook_commands.append('    ruff check --fix $python_files')
            hook_commands.append('  fi')
        elif hook == "black":
            hook_commands.append('  if [ -n "$python_files" ]; then')
            hook_commands.append('    black --check $python_files')
            hook_commands.append('  fi')
        elif hook == "isort":
            hook_commands.append('  if [ -n "$python_files" ]; then')
            hook_commands.append('    isort --check-only $python_files')
            hook_commands.append('  fi')
        elif hook == "trailing-whitespace":
            hook_commands.append('  if git diff --cached --check | grep -q \'trailing whitespace\'; then')
            hook_commands.append('    echo "Trailing whitespace detected!"')
            hook_commands.append('    exit 1')
            hook_commands.append('  fi')

    hook_body = "\n".join(hook_commands)
    hook_content = PRE_COMMIT_HOOK_TEMPLATE.replace("{hooks}", hook_body)
    write_file(hook_path, hook_content, mode="x")


def create_git_message(project_path: Path, global_template: bool = False):
    target = (project_path / ".gitmessage") if not global_template else Path.home() / ".gitmessage"
    write_file(target, GITMESSAGE)


def init_git_repo(project_path: Path):
    subprocess.run(["git", "init"], cwd=str(project_path), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run(["git", "add", "."], cwd=str(project_path), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run(
        ["git", "commit", "-m", "Initial commit: scaffold"],
        cwd=str(project_path),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )


def install_global_template():
    template_dir = Path.home() / ".git-templates"
    template_dir.mkdir(parents=True, exist_ok=True)

    # Hook
    hook_dir = template_dir / "hooks"
    hook_dir.mkdir(parents=True, exist_ok=True)
    write_file(hook_dir / "pre-commit", PRE_COMMIT_HOOK, mode="x")

    # Commit message template
    write_file(Path.home() / ".gitmessage", GITMESSAGE)

    # Register with Git
    subprocess.run(["git", "config", "--global", "init.templateDir", str(template_dir)],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    print("✅ Global Git template installed at:", template_dir)

# ----------------------------------------------------------------------
# Main scaffolder logic
# ----------------------------------------------------------------------
def scaffold(project_name: str, base_path: str, template: str):
    base = Path(base_path).expanduser().resolve()
    project_dir = base / project_name
    if project_dir.exists():
        print(f"❌ Directory {project_dir} already exists – aborting.")
        sys.exit(1)

    tmpl = TEMPLATES.get(template, TEMPLATES["default"])

    # ------------------------------------------------------------------
    # 1️⃣ Create directories
    # ------------------------------------------------------------------
    for d in tmpl["dirs"]:
        d = d.replace("{package_name}", project_name.replace("-", "_"))
        (project_dir / d).mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # 2️⃣ Populate static files
    # ------------------------------------------------------------------
    write_file(project_dir / ".claudeignore", CLAUDEIGNORE)
    write_file(project_dir / ".gitignore", GITIGNORE)
    write_file(project_dir / "README.md", f"""# {project_name}
Version: {VERSION}
Codename: {CODENAME}
Generated on: {datetime.now(timezone.utc).isoformat()} UTC

## Quick start
```bash
cd {project_name}
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
""")

    reqs = tmpl.get("extra_deps", [])
    write_file(project_dir / "requirements.txt", "\n".join(reqs) + "\n")

    workflow_paths = [".github/workflows/pipeline.yml"]
    configured_workflow = settings.get("ci.pipeline_file", ".github/workflows/pipeline.yml")
    if configured_workflow not in workflow_paths:
        workflow_paths.append(configured_workflow)

    for workflow_rel_path in workflow_paths:
        workflow_file = project_dir / workflow_rel_path
        workflow_file.parent.mkdir(parents=True, exist_ok=True)
        write_file(workflow_file, WORKFLOW_YAML_TEMPLATE)

    # ------------------------------------------------------------------
    # 3️⃣ Template-specific files
    # ------------------------------------------------------------------
    for rel_path, content in tmpl["files"].items():
        rel_path = rel_path.replace("{package_name}", project_name.replace("-", "_"))
        filled = render_template(content,
                                 project_name=project_name,
                                 version=VERSION,
                                 package_name=project_name.replace("-", "_"))
        write_file(project_dir / rel_path, filled)

    # ------------------------------------------------------------------
    # 4️⃣ Git init + hooks
    # ------------------------------------------------------------------
    init_git_repo(project_dir)
    create_git_hook(project_dir, global_template=False)
    create_git_message(project_dir, global_template=False)

    print(f"✅ Project {project_name} created at {project_dir}")
    print("\n🚀 Next steps:")
    print(f"   cd {project_name}")
    print("   source venv/bin/activate   # if you created a venv")
    print("   pip install -r requirements.txt")
    print("   git commit -m 'feat: initial scaffold'   # test hooks")
    return project_dir

# ----------------------------------------------------------------------
# CLI entry point
# ----------------------------------------------------------------------
VERSION = "0.2.2"
CODENAME = "Waddler OS Pro"

def main():
    parser = argparse.ArgumentParser(
        prog="hatch",
        description="God Mode Scaffolder – rapid, secure Python project bootstrapper"
    )
    parser.add_argument("project_name", nargs="?", help="Name of the project directory")
    parser.add_argument("-p", "--path", default=".", help="Base path where the project will be created")
    parser.add_argument("-t", "--template", choices=["cli", "web", "lib"], default="cli",
                        help="Template to use (default: cli)")
    parser.add_argument("--setup-global", action="store_true",
                        help="Install global Git template & hooks for all future repos")
    parser.add_argument("--version", action="store_true", help="Show version and exit")

    args = parser.parse_args()

    if args.version:
        print(f"hatch.py {VERSION} ({CODENAME})")
        sys.exit(0)

    if args.setup_global:
        install_global_template()
        sys.exit(0)

    if not args.project_name:
        parser.error("project_name is required unless --setup-global is used")

    scaffold(args.project_name, args.path, args.template)


if __name__ == '__main__':
    main()
