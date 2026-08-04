"""Adapter policy configuration loader.

Loads adapters.yaml from the stunning-octo-funicular repository root (two levels up
from this module) and provides get_policy(adapter_name) to return a policy dict.

Policy schema (YAML):

policies:
  god_stack:
    allowed_args: ['--exec']
    timeout_seconds: 120
  default:
    allowed_args: ['--exec']
    timeout_seconds: 60

"""
from pathlib import Path
from typing import Dict, Any
import yaml


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def load_policies() -> Dict[str, Any]:
    root = _repo_root()
    cfg = root / "adapters.yaml"
    if not cfg.exists():
        return {}
    try:
        data = yaml.safe_load(cfg.read_text(encoding="utf-8")) or {}
        return data.get("policies", {})
    except Exception:
        return {}


_POLICIES = None


def get_policy(name: str) -> Dict[str, Any]:
    global _POLICIES
    if _POLICIES is None:
        _POLICIES = load_policies()
    return _POLICIES.get(name, _POLICIES.get("default", {}))
