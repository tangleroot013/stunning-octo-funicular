from src.plugins.discover import discover_adapters_in_paths
from src.plugins.runner import run_adapter
from pathlib import Path
import os


def test_discover_in_paths_tmp(tmp_path):
    # create a fake adapter file
    repo = tmp_path / "fake-repo"
    repo.mkdir()
    adapter_file = repo / "stunning_octo_adapter.py"
    adapter_file.write_text("""class FakeAdapter:\n    name = 'fake-repo'\n    description = 'fake'\n    def run(self, args):\n        return 0\n\nadapter = FakeAdapter()\n""")
    adapters = discover_adapters_in_paths([str(repo)])
    names = [a.name for a in adapters]
    assert 'fake-repo' in names


def test_run_adapter_disallows_args():
    # Use an existing adapter (god_stack) as example
    from src.plugins.adapters.god_stack_adapter import adapter as g_adapter
    rc, timed_out, err = run_adapter(g_adapter, ['--dangerous'], timeout_seconds=1, allowed_args=['--exec'])
    assert rc == 3 or err is not None


def test_run_adapter_timeout(tmp_path):
    # adapter that sleeps longer than timeout
    adapter_file = tmp_path / 'stunning_octo_adapter.py'
    adapter_file.write_text("""import time\nclass SlowAdapter:\n    name='slow'\n    description='slow'\n    def run(self, args):\n        time.sleep(2)\n        return 0\nadapter=SlowAdapter()\n""")
    adapters = discover_adapters_in_paths([str(tmp_path)])
    slow = [a for a in adapters if a.name=='slow'][0]
    rc, timed_out, err = run_adapter(slow, ['--exec'], timeout_seconds=0.5, allowed_args=['--exec'])
    assert timed_out is True
