import pytest
from unittest.mock import patch, MagicMock

from src.plugins.adapters.development_adapter import DevelopmentAdapter
from src.plugins.adapters.god_stack_adapter import GodStackAdapter
from src.plugins.adapters.metaclean_adapter import MetaCleanAdapter
from src.plugins.adapters.my_web_api_adapter import MyWebApiAdapter
from src.plugins.adapters.penguin_diag_adapter import PenguinDiagAdapter
from src.plugins.adapters.scripts_adapter import ScriptsAdapter


@pytest.fixture
def dev_adapter():
    return DevelopmentAdapter()

@pytest.fixture
def god_adapter():
    return GodStackAdapter()

@pytest.fixture
def metaclean_adapter():
    return MetaCleanAdapter()

@pytest.fixture
def my_web_api_adapter():
    return MyWebApiAdapter()

@pytest.fixture
def penguin_diag_adapter():
    return PenguinDiagAdapter()

@pytest.fixture
def scripts_adapter():
    return ScriptsAdapter()


# --- Development Adapter Tests ---

@patch('src.plugins.adapters.development_adapter.Path')
def test_development_repo_not_found(mock_path, dev_adapter):
    mock_path.return_value.exists.return_value = False
    assert dev_adapter.run([]) == 2

@patch('src.plugins.adapters.development_adapter.Path')
def test_development_dry_run(mock_path, dev_adapter):
    mock_path.return_value.exists.return_value = True
    assert dev_adapter.run([]) == 0

@patch('src.plugins.adapters.development_adapter.subprocess.run')
@patch('src.plugins.adapters.development_adapter.Path')
def test_development_exec_with_pytest(mock_path, mock_run, dev_adapter):
    mock_repo = MagicMock()
    mock_repo.exists.return_value = True
    mock_repo.__truediv__.return_value.exists.return_value = True
    mock_path.return_value = mock_repo
    mock_run.return_value.returncode = 0
    assert dev_adapter.run(["--exec"]) == 0
    mock_run.assert_called_once()

@patch('src.plugins.adapters.development_adapter.subprocess.run')
@patch('src.plugins.adapters.development_adapter.Path')
def test_development_exec_without_pytest(mock_path, mock_run, dev_adapter):
    mock_repo = MagicMock()
    mock_repo.exists.return_value = True
    mock_repo.__truediv__.return_value.exists.return_value = False
    mock_path.return_value = mock_repo
    mock_run.return_value.returncode = 0
    assert dev_adapter.run(["--exec"]) == 0
    mock_run.assert_called_once()


# --- God Stack Adapter Tests ---

@patch('src.plugins.adapters.god_stack_adapter.Path')
def test_god_stack_repo_not_found(mock_path, god_adapter):
    mock_path.return_value.exists.return_value = False
    assert god_adapter.run([]) == 2

@patch('src.plugins.adapters.god_stack_adapter.Path')
def test_god_stack_dry_run(mock_path, god_adapter):
    mock_path.return_value.exists.return_value = True
    assert god_adapter.run([]) == 0

@patch('src.plugins.adapters.god_stack_adapter.subprocess.run')
@patch('src.plugins.adapters.god_stack_adapter.Path')
def test_god_stack_exec(mock_path, mock_run, god_adapter):
    mock_repo = MagicMock()
    mock_repo.exists.return_value = True
    mock_path.return_value = mock_repo
    mock_run.return_value.returncode = 0
    assert god_adapter.run(["--exec"]) == 0
    mock_run.assert_called_once()


# --- MetaClean Adapter Tests ---

@patch('src.plugins.adapters.metaclean_adapter.Path')
def test_metaclean_repo_not_found(mock_path, metaclean_adapter):
    mock_path.return_value.exists.return_value = False
    assert metaclean_adapter.run([]) == 2

@patch('src.plugins.adapters.metaclean_adapter.Path')
def test_metaclean_dry_run(mock_path, metaclean_adapter):
    mock_path.return_value.exists.return_value = True
    assert metaclean_adapter.run([]) == 0

@patch('src.plugins.adapters.metaclean_adapter.subprocess.run')
@patch('src.plugins.adapters.metaclean_adapter.Path')
def test_metaclean_exec(mock_path, mock_run, metaclean_adapter):
    mock_path.return_value.exists.return_value = True
    mock_run.return_value.returncode = 0
    assert metaclean_adapter.run(["--exec"]) == 0
    mock_run.assert_called_once()


# --- My Web API Adapter Tests ---

@patch('src.plugins.adapters.my_web_api_adapter.Path')
def test_my_web_api_repo_not_found(mock_path, my_web_api_adapter):
    mock_path.return_value.exists.return_value = False
    assert my_web_api_adapter.run([]) == 2

@patch('src.plugins.adapters.my_web_api_adapter.Path')
def test_my_web_api_dry_run(mock_path, my_web_api_adapter):
    mock_path.return_value.exists.return_value = True
    assert my_web_api_adapter.run([]) == 0

@patch('src.plugins.adapters.my_web_api_adapter.subprocess.run')
@patch('src.plugins.adapters.my_web_api_adapter.Path')
def test_my_web_api_exec(mock_path, mock_run, my_web_api_adapter):
    mock_path.return_value.exists.return_value = True
    mock_run.return_value.returncode = 0
    assert my_web_api_adapter.run(["--exec"]) == 0
    mock_run.assert_called_once()


# --- Penguin Diag Adapter Tests ---

@patch('src.plugins.adapters.penguin_diag_adapter.Path')
def test_penguin_diag_repo_not_found(mock_path, penguin_diag_adapter):
    mock_path.return_value.exists.return_value = False
    assert penguin_diag_adapter.run([]) == 2

@patch('src.plugins.adapters.penguin_diag_adapter.Path')
def test_penguin_diag_dry_run(mock_path, penguin_diag_adapter):
    mock_path.return_value.exists.return_value = True
    assert penguin_diag_adapter.run([]) == 0

@patch('src.plugins.adapters.penguin_diag_adapter.subprocess.run')
@patch('src.plugins.adapters.penguin_diag_adapter.Path')
def test_penguin_diag_exec(mock_path, mock_run, penguin_diag_adapter):
    mock_path.return_value.exists.return_value = True
    mock_run.return_value.returncode = 0
    assert penguin_diag_adapter.run(["--exec"]) == 0
    mock_run.assert_called_once()


# --- Scripts Adapter Tests ---

@patch('src.plugins.adapters.scripts_adapter.Path')
def test_scripts_repo_not_found(mock_path, scripts_adapter):
    mock_path.return_value.exists.return_value = False
    assert scripts_adapter.run([]) == 2

@patch('src.plugins.adapters.scripts_adapter.Path')
def test_scripts_dry_run(mock_path, scripts_adapter):
    mock_path.return_value.exists.return_value = True
    assert scripts_adapter.run([]) == 0

@patch('src.plugins.adapters.scripts_adapter.subprocess.run')
@patch('src.plugins.adapters.scripts_adapter.Path')
def test_scripts_exec(mock_path, mock_run, scripts_adapter):
    mock_path.return_value.exists.return_value = True
    mock_run.return_value.returncode = 0
    assert scripts_adapter.run(["--exec"]) == 0
    mock_run.assert_called_once()
