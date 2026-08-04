"""Plugins package for stunning-octo-funicular adapters.

Adapters live under src.plugins.adapters and expose an `adapter` object
that follows the PluginProtocol in interface.py.

This package exposes discovery helpers and a safe runner for executing
adapters under policy.
"""
from .discover import discover_adapters, discover_adapters_in_paths
from .runner import run_adapter

__all__ = ["discover_adapters", "discover_adapters_in_paths", "run_adapter"]
