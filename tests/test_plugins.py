import os
from src.plugins.discover import discover_adapters


def test_discover_adapters():
    adapters = discover_adapters()
    names = [getattr(a, "name", None) for a in adapters]
    # expect at least our example adapters to be present
    assert "god_stack" in names
    assert "metaclean" in names


def test_adapter_dry_run():
    adapters = discover_adapters()
    for a in adapters:
        rc = a.run([])
        assert rc == 0
