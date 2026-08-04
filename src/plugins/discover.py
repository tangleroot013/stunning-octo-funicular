"""Discover and load plugin adapters.

This discoverer supports two modes:
- Package-based discovery: existing modules under src.plugins.adapters
- Path-based discovery: given a list of repository root paths, look for a
  `stunning_octo_adapter.py` module at the repo root and import it by file.

Adapters are expected to export an `adapter` object that matches PluginProtocol.
"""
import importlib
import importlib.util
import pkgutil
from pathlib import Path
from typing import List

from .interface import PluginProtocol


def _load_adapter_from_module(mod) -> List[PluginProtocol]:
    found = []
    adapter = getattr(mod, "adapter", None)
    if adapter is not None and isinstance(adapter, PluginProtocol):
        found.append(adapter)
    return found


def discover_adapters() -> List[PluginProtocol]:
    """Discover adapters from the bundled src.plugins.adapters package."""
    adapters: List[PluginProtocol] = []
    package_name = "src.plugins.adapters"
    try:
        pkg = importlib.import_module(package_name)
    except Exception:
        return adapters

    for finder, name, ispkg in pkgutil.iter_modules(pkg.__path__):
        full_name = f"{package_name}.{name}"
        try:
            mod = importlib.import_module(full_name)
        except Exception:
            continue
        adapters.extend(_load_adapter_from_module(mod))
    return adapters


def discover_adapters_in_paths(paths: List[str]) -> List[PluginProtocol]:
    """Discover adapters by scanning provided filesystem paths.

    For each path, if a file named `stunning_octo_adapter.py` exists at the
    repository root, import it (by file) and collect its `adapter` export.
    """
    adapters: List[PluginProtocol] = []
    for p in paths:
        try:
            repo_root = Path(p).expanduser().resolve()
        except Exception:
            continue
        candidate = repo_root / "stunning_octo_adapter.py"
        if not candidate.exists():
            continue
        module_name = f"stunning_octo_adapter_{repo_root.name}"
        try:
            spec = importlib.util.spec_from_file_location(module_name, str(candidate))
            if spec and spec.loader:
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                adapters.extend(_load_adapter_from_module(mod))
        except Exception:
            continue
    return adapters
