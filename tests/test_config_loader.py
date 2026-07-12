"""Tests for src/utils/config_loader.py — closes coverage gaps at
lines 19-22, 51, 59, 67."""
import json
import pathlib
import pytest

from src.utils import config_loader
from src.utils.config_loader import _load_json, _merge_dicts, settings


@pytest.fixture(autouse=True)
def isolate_settings_state():
    """Settings._data is class-level mutable state shared across the whole
    test session. Snapshot and restore it (and _ROOT) after every test in
    this file so we don't leak into other test modules."""
    original_data = dict(settings._data)
    original_root = config_loader._ROOT
    yield
    settings._data = original_data
    config_loader._ROOT = original_root


def test_load_json_returns_empty_dict_for_nonexistent_file():
    assert _load_json(pathlib.Path("/nonexistent/file.json")) == {}


def test_merge_dicts_recurses_into_nested_dicts_and_overrides_scalars():
    """Lines 19-22: dict values merge recursively, non-dict values overwrite."""
    base = {"a": {"b": 1}, "c": 2}
    overlay = {"a": {"b": 3, "d": 4}, "c": 5, "e": 6}
    result = _merge_dicts(base, overlay)
    assert result == {"a": {"b": 3, "d": 4}, "c": 5, "e": 6}


def test_settings_load_raises_on_missing_required_sections(tmp_path, monkeypatch):
    """Line 51: missing required top-level sections raises RuntimeError."""
    monkeypatch.setattr(config_loader, "_ROOT", tmp_path)
    settings_file = tmp_path / "settings.json"
    settings_file.write_text(json.dumps({"repository": {}}), encoding="utf-8")

    with pytest.raises(RuntimeError) as exc_info:
        settings.load()
    assert "Missing required configuration sections" in str(exc_info.value)


def test_settings_get_auto_loads_when_data_is_empty(tmp_path, monkeypatch):
    """Line 59: .get() calls .load() automatically if _data is empty."""
    monkeypatch.setattr(config_loader, "_ROOT", tmp_path)
    valid_data = {sec: {} for sec in ["repository", "github", "ci", "web", "library", "testing"]}
    valid_data["repository"]["name"] = "auto-loaded-repo"
    (tmp_path / "settings.json").write_text(json.dumps(valid_data), encoding="utf-8")

    settings._data = {}
    val = settings.get("repository.name")
    assert val == "auto-loaded-repo"


def test_settings_get_returns_default_on_missing_dotted_path():
    """Line 67: an unresolvable dotted path returns the provided default."""
    settings._data = {"repository": {"name": "test"}}
    assert settings.get("repository.nonexistent", "fallback_val") == "fallback_val"
    assert settings.get("nonexistent.path", "fallback_val") == "fallback_val"


def test_settings_get_walks_multiple_nested_levels():
    """Sanity check on the normal-path loop in .get() (lines 61-66)."""
    settings._data = {"a": {"b": {"c": "deep_value"}}}
    assert settings.get("a.b.c") == "deep_value"
