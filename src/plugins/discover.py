"""Discover and load plugin adapters from the adapters package.

This simple discoverer imports all modules under src.plugins.adapters and
collects any `adapter` attribute exported by those modules.
"""
import importlib
import pkgutil
from typing import List

from .interface import PluginProtocol


def discover_adapters() -> List[PluginProtocol]:
    adapters = []
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
        # adapters expose an `adapter` object
        adapter = getattr(mod, "adapter", None)
        if adapter is not None and isinstance(adapter, PluginProtocol):
            adapters.append(adapter)
    return adapters
