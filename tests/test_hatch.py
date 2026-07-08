from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import hatch
from src.utils.ai_collab import build_llm_payload
from src.utils.config_loader import Settings


def test_scaffold_generates_ci_and_hook_templates(tmp_path, monkeypatch):
    monkeypatch.setattr(hatch, "init_git_repo", lambda project_path: None)

    project_dir = hatch.scaffold("demo-app", str(tmp_path), "cli")

    assert project_dir == tmp_path / "demo-app"
    assert (project_dir / ".claudeignore").exists()
    assert (project_dir / ".gitignore").exists()
    assert (project_dir / "requirements.txt").exists()

    workflow = (project_dir / ".github" / "workflows" / "pipeline.yml").read_text(encoding="utf-8")
    assert "lint-and-format" in workflow
    assert "ruff check" in workflow
    assert "pytest --cov ." in workflow

    hook = (project_dir / ".git" / "hooks" / "pre-commit").read_text(encoding="utf-8")
    assert "QUACK! Secret detected in staged changes!" in hook
    assert "ruff check --fix" in hook
    assert "black --check" in hook
    assert "isort --check-only" in hook


def test_settings_loader_reads_repository_configuration():
    Settings._data = {}
    Settings.load()

    assert Settings.get("ci.pre_commit.hooks", []) == [
        "detect-secrets",
        "py_compile",
        "ruff",
        "black",
        "isort",
        "trailing-whitespace",
    ]
    assert Settings.get("ci.pipeline_file", ".github/workflows/pipeline.yml") == ".github/workflows/ci.yml"


def test_build_llm_payload_respects_token_efficient_rules():
    payload = build_llm_payload()

    assert payload["system_prompt"]
    assert payload["user_prompt"]
    assert payload["files"]
    assert all("tests/" not in entry["path"] for entry in payload["files"])
    assert all("docs/" not in entry["path"] for entry in payload["files"])


def test_web_and_lib_templates_include_pro_boilerplate(tmp_path, monkeypatch):
    monkeypatch.setattr(hatch, "init_git_repo", lambda project_path: None)

    web_dir = hatch.scaffold("web-demo", str(tmp_path), "web")
    assert (web_dir / "src" / "core" / "config.py").exists()
    config = (web_dir / "src" / "core" / "config.py").read_text(encoding="utf-8")
    assert "BaseSettings" in config
    assert "APP_NAME" in config

    lib_dir = hatch.scaffold("lib-demo", str(tmp_path), "lib")
    core = (lib_dir / "src" / "lib_demo" / "core.py").read_text(encoding="utf-8")
    assert "validate_swim_distance" in core
    assert "Ducks cannot swim backwards" in core
