"""Plugins package for stunning-octo-funicular adapters.

Adapters live under src.plugins.adapters and expose an `adapter` object
that follows the PluginProtocol in interface.py.
"""
from .discover import discover_adapters

__all__ = ["discover_adapters"]
