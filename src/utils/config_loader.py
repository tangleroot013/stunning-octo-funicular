import json
import pathlib
from typing import Any, List

_ROOT = pathlib.Path(__file__).resolve().parents[2]


def _load_json(file_path: pathlib.Path) -> dict:
    """Safely load a JSON file; return {} when the file does not exist."""
    if not file_path.is_file():
        return {}
    with file_path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def _merge_dicts(base: dict, overlay: dict) -> dict:
    """Recursively merge overlay into base, overriding values."""
    for key, value in overlay.items():
        if isinstance(value, dict) and isinstance(base.get(key), dict):
            base[key] = _merge_dicts(base.get(key, {}), value)
        else:
            base[key] = value
    return base


class Settings:
    """Singleton-style accessor for repository configuration."""

    _data: dict = {}

    @classmethod
    def load(cls) -> None:
        """Read settings.json and optional local overrides."""
        default_path = _ROOT / "settings.json"
        local_path = _ROOT / "settings.local.json"

        base = _load_json(default_path)
        overlay = _load_json(local_path)
        cls._data = _merge_dicts(base, overlay)

        required_sections: List[str] = [
            "repository",
            "github",
            "ci",
            "web",
            "library",
            "testing",
        ]
        missing = [sec for sec in required_sections if sec not in cls._data]
        if missing:
            raise RuntimeError(
                f"Missing required configuration sections in settings.json: {missing}"
            )

    @classmethod
    def get(cls, path: str, default: Any = None) -> Any:
        """Retrieve a value using a dotted path, e.g. 'ci.pre_commit.hooks'."""
        if not cls._data:
            cls.load()

        keys = path.split(".")
        cur: Any = cls._data
        for key in keys:
            if isinstance(cur, dict) and key in cur:
                cur = cur[key]
            else:
                return default
        return cur


settings = Settings
