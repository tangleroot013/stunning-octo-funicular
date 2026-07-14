import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src import hatch
from src.utils.ai_collab import build_llm_payload
from src.utils.config_loader import Settings
from src.utils.snapshot import build_context_snapshot


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


def test_build_context_snapshot_creates_markdown_output(tmp_path):
    output_path = build_context_snapshot(root_dir=tmp_path)

    assert output_path.exists()
    assert output_path.name == "project_snapshot.md"
    content = output_path.read_text(encoding="utf-8")
    assert "# Project Context Snapshot" in content
    assert "## Files" in content


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


# ────────────────────────────── coverage gap fills ──────────────────────────────

import argparse as _argparse


class _FakeSettings:
    def __init__(self, data):
        self._data = data

    def get(self, key, default=None):
        return self._data.get(key, default)


def test_valid_coverage_threshold_non_integer():
    with pytest.raises(_argparse.ArgumentTypeError):
        hatch._valid_coverage_threshold("abc")


def test_valid_coverage_threshold_out_of_range():
    with pytest.raises(_argparse.ArgumentTypeError):
        hatch._valid_coverage_threshold("150")


def test_create_git_hook_isort_and_trailing_whitespace(tmp_path, monkeypatch):
    monkeypatch.setattr(
        hatch, "settings",
        _FakeSettings({"ci.pre_commit.hooks": ["isort", "trailing-whitespace"]}),
    )
    project_dir = tmp_path / "proj"
    project_dir.mkdir()
    hatch.create_git_hook(project_dir, global_template=False)
    hook_path = project_dir / ".git" / "hooks" / "pre-commit"
    content = hook_path.read_text()
    assert "isort --check-only" in content
    assert "Trailing whitespace detected" in content


def test_init_git_repo_runs_real_git(tmp_path):
    project_dir = tmp_path / "proj"
    project_dir.mkdir()
    hatch.init_git_repo(project_dir)
    assert (project_dir / ".git").exists()


def test_install_global_template(tmp_path, monkeypatch):
    monkeypatch.setattr(hatch.Path, "home", lambda: tmp_path)
    monkeypatch.setattr(hatch.subprocess, "run", lambda *a, **k: None)
    hatch.install_global_template()
    assert (tmp_path / ".git-templates" / "hooks" / "pre-commit").exists()
    assert (tmp_path / ".gitmessage").exists()


def test_scaffold_already_exists(tmp_path):
    (tmp_path / "myproj").mkdir()
    with pytest.raises(SystemExit) as exc:
        hatch.scaffold("myproj", str(tmp_path), "cli")
    assert exc.value.code == 1


def test_scaffold_sync_failure_and_extra_workflow(tmp_path, monkeypatch):
    monkeypatch.setattr(
        hatch, "settings",
        _FakeSettings({
            "ci.pre_commit.hooks": [],
            "ci.pipeline_file": ".github/workflows/custom.yml",
        }),
    )
    monkeypatch.setattr(hatch, "sync_ignore_files", lambda root_dir, verbose=False: (False, "boom"))
    project_dir = hatch.scaffold("myproj2", str(tmp_path), "cli")
    assert (project_dir / ".github" / "workflows" / "pipeline.yml").exists()
    assert (project_dir / ".github" / "workflows" / "custom.yml").exists()


def test_run_wizard_keyboard_interrupt(monkeypatch):
    def _raise(defaults=None):
        raise KeyboardInterrupt
    monkeypatch.setattr(hatch, "collect_answers", _raise)
    with pytest.raises(SystemExit) as exc:
        hatch.run_wizard()
    assert exc.value.code == 0


def test_run_wizard_setup_global(monkeypatch):
    monkeypatch.setattr(
        hatch, "collect_answers",
        lambda defaults=None: {"setup_global": True, "project_name": "x", "base_path": ".", "template": "cli", "coverage_threshold": 85},
    )
    monkeypatch.setattr(hatch, "scaffold", lambda **kw: None)
    called = {}
    monkeypatch.setattr(hatch, "install_global_template", lambda: called.setdefault("yes", True))
    hatch.run_wizard()
    assert called.get("yes") is True


def test_main_version(monkeypatch, capsys):
    monkeypatch.setattr(hatch.sys, "argv", ["hatch.py", "--version"])
    with pytest.raises(SystemExit) as exc:
        hatch.main()
    assert exc.value.code == 0
    assert "hatch.py" in capsys.readouterr().out


def test_main_sync_ignores_success(monkeypatch, tmp_path):
    monkeypatch.setattr(hatch.sys, "argv", ["hatch.py", "--sync-ignores", "--path", str(tmp_path)])
    monkeypatch.setattr(hatch, "sync_ignore_files", lambda root_dir, verbose, dry_run: (True, "synced"))
    with pytest.raises(SystemExit) as exc:
        hatch.main()
    assert exc.value.code == 0


def test_main_sync_ignores_failure(monkeypatch, tmp_path):
    monkeypatch.setattr(hatch.sys, "argv", ["hatch.py", "--sync-ignores", "--path", str(tmp_path)])
    monkeypatch.setattr(hatch, "sync_ignore_files", lambda root_dir, verbose, dry_run: (False, "nope"))
    with pytest.raises(SystemExit) as exc:
        hatch.main()
    assert exc.value.code == 1


def test_main_sync_ignores_exception(monkeypatch, tmp_path):
    monkeypatch.setattr(hatch.sys, "argv", ["hatch.py", "--sync-ignores", "--path", str(tmp_path)])
    def _raise(root_dir, verbose, dry_run):
        raise hatch.SyncIgnoresError("bad")
    monkeypatch.setattr(hatch, "sync_ignore_files", _raise)
    with pytest.raises(SystemExit) as exc:
        hatch.main()
    assert exc.value.code == 1


def test_main_setup_global(monkeypatch):
    monkeypatch.setattr(hatch.sys, "argv", ["hatch.py", "--setup-global"])
    called = {}
    monkeypatch.setattr(hatch, "install_global_template", lambda: called.setdefault("yes", True))
    with pytest.raises(SystemExit) as exc:
        hatch.main()
    assert exc.value.code == 0
    assert called.get("yes") is True
