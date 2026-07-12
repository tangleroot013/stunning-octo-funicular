"""Tests for src/utils/ai_collab.py — closes coverage gaps at
lines 17, 37, 39, 83, 95-96."""
import pathlib
import pytest

from src.utils import ai_collab, config_loader
from src.utils.ai_collab import PromptTemplates, WorkspaceFilter, build_llm_payload
from src.utils.config_loader import settings


@pytest.fixture(autouse=True)
def isolate_settings_state():
    original_data = dict(settings._data)
    original_templates = dict(PromptTemplates._templates)
    original_repo_root = WorkspaceFilter._repo_root
    yield
    settings._data = original_data
    PromptTemplates._templates = original_templates
    WorkspaceFilter._repo_root = original_repo_root


def test_prompt_templates_load_raises_when_not_a_mapping(monkeypatch):
    """Line 17: non-dict templates value raises RuntimeError."""
    monkeypatch.setattr(settings, "_data", {"ai_collaboration": {"templates": "not-a-dict"}})
    PromptTemplates._templates = {}
    with pytest.raises(RuntimeError, match="must be a mapping"):
        PromptTemplates.load()


def test_workspace_filter_falls_back_to_exclude_globs(monkeypatch):
    """Line 37: empty claudeignore patterns fall back to exclude_globs key."""
    monkeypatch.setattr(settings, "_data", {
        "workspace": {"ignore_patterns": {"claudeignore": []}},
        "ai_collaboration": {"directory_scanning_protection": {"exclude_globs": ["*.tmp"]}},
    })
    rules = WorkspaceFilter._load_rules()
    assert rules["exclude_patterns"] == ["*.tmp"]


def test_workspace_filter_coerces_non_list_patterns_to_empty(monkeypatch):
    """Line 39: a non-list patterns value resets to []."""
    monkeypatch.setattr(settings, "_data", {
        "workspace": {"ignore_patterns": {"claudeignore": "not-a-list"}},
        "ai_collaboration": {"directory_scanning_protection": {"exclude_globs": "also-not-a-list"}},
    })
    rules = WorkspaceFilter._load_rules()
    assert rules["exclude_patterns"] == []


def test_build_llm_payload_falls_back_to_strict_on_invalid_mode(monkeypatch, tmp_path):
    """Line 83: an unrecognized token_efficiency_mode value resets to 'strict'."""
    monkeypatch.setattr(WorkspaceFilter, "_repo_root", tmp_path)
    monkeypatch.setattr(settings, "_data", {
        "ai_collaboration": {"token_efficiency_mode": "chaotic-invalid-value"},
    })
    payload = build_llm_payload()
    assert payload["system_prompt"] == "You are a helpful AI assistant."


def test_build_llm_payload_relaxed_mode_collects_files(monkeypatch, tmp_path):
    """Lines 95-96: relaxed mode scans cwd directly instead of WorkspaceFilter."""
    (tmp_path / "keep.py").write_text("print('hi')")
    (tmp_path / "skip.tmp").write_text("junk")

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(WorkspaceFilter, "_repo_root", tmp_path)
    monkeypatch.setattr(settings, "_data", {
        "ai_collaboration": {
            "token_efficiency_mode": "relaxed",
            "directory_scanning_protection": {"exclude_globs": ["*.tmp"]},
        },
    })

    payload = build_llm_payload()
    paths = [f["path"] for f in payload["files"]]
    assert "keep.py" in paths
    assert "skip.tmp" not in paths
