import sys
import pytest
from utils.wizard import (
    ask,
    choose,
    yes_no,
    collect_answers,
    is_valid_project_name,
    is_valid_coverage,
    DEFAULT_COVERAGE_THRESHOLD,
    TEMPLATE_CHOICES,
)


class TestValidators:
    @pytest.mark.parametrize("name,expected", [
        ("my-project", True),
        ("my_project", True),
        ("MyProject", True),
        ("a", True),
        ("123project", False),
        ("", False),
        ("my project", False),
        ("my/project", False),
    ])
    def test_project_name_validator(self, name, expected):
        assert is_valid_project_name(name) is expected

    @pytest.mark.parametrize("value,expected", [
        ("0", True),
        ("50", True),
        ("100", True),
        ("85", True),
        ("-1", False),
        ("101", False),
        ("abc", False),
        ("", False),
    ])
    def test_coverage_validator(self, value, expected):
        assert is_valid_coverage(value) is expected


class TestAsk:
    def test_ask_uses_default_on_empty_input(self, monkeypatch):
        monkeypatch.setattr("builtins.input", lambda: "")
        assert ask("Name", default="default-name") == "default-name"

    def test_ask_rejects_invalid_and_retries(self, monkeypatch, capsys):
        inputs = iter(["bad", "good"])
        monkeypatch.setattr("builtins.input", lambda: next(inputs))
        result = ask(
            "Name",
            default=None,
            validator=lambda x: x == "good",
            validation_error_msg="Nope",
        )
        assert result == "good"
        captured = capsys.readouterr()
        assert "Nope" in captured.out

    def test_ask_loops_when_empty_and_no_default(self, monkeypatch):
        inputs = iter(["", "", "finally"])
        monkeypatch.setattr("builtins.input", lambda: next(inputs))
        assert ask("Name", default=None) == "finally"


class TestChoose:
    def test_choose_by_number(self, monkeypatch):
        monkeypatch.setattr("builtins.input", lambda: "2")
        assert choose("Pick", TEMPLATE_CHOICES) == "web"

    def test_choose_uses_default_on_empty_input(self, monkeypatch):
        monkeypatch.setattr("builtins.input", lambda: "")
        assert choose("Pick", TEMPLATE_CHOICES, default="lib") == "lib"

    def test_choose_rejects_invalid_input(self, monkeypatch, capsys):
        inputs = iter(["99", "abc", "1"])
        monkeypatch.setattr("builtins.input", lambda: next(inputs))
        result = choose("Pick", TEMPLATE_CHOICES)
        assert result == "cli"
        captured = capsys.readouterr()
        assert "Please enter a number" in captured.out


class TestYesNo:
    def test_yes_no_defaults(self, monkeypatch):
        monkeypatch.setattr("builtins.input", lambda: "")
        assert yes_no("Go?", default=True) is True
        assert yes_no("Go?", default=False) is False

    def test_yes_no_returns_true_on_affirmative_variants(self, monkeypatch):
        for val in ["y", "yes", "true", "1", "Y", "YES"]:
            monkeypatch.setattr("builtins.input", lambda v=val: v)
            assert yes_no("Go?") is True

    def test_yes_no_reprompts_on_invalid_input(self, monkeypatch, capsys):
        inputs = iter(["maybe", "y"])
        monkeypatch.setattr("builtins.input", lambda: next(inputs))
        assert yes_no("Go?") is True
        captured = capsys.readouterr()
        assert "Please answer yes/y or no/n" in captured.out


class TestCollectAnswers:
    def test_collect_answers(self, monkeypatch):
        inputs = iter(["test-project", "2", ".", "90", "y"])
        monkeypatch.setattr("builtins.input", lambda: next(inputs))
        res = collect_answers()
        assert res["project_name"] == "test-project"
        assert res["template"] == "web"
        assert res["coverage_threshold"] == 90
        assert res["setup_global"] is True

    def test_collect_answers_resets_invalid_coverage_default(self, monkeypatch):
        inputs = iter(["test-project", "1", ".", "85", "n"])
        monkeypatch.setattr("builtins.input", lambda: next(inputs))
        res = collect_answers({"coverage_threshold": "not-an-int"})
        assert res["coverage_threshold"] == DEFAULT_COVERAGE_THRESHOLD
        assert res["project_name"] == "test-project"

    def test_collect_answers_keyboard_interrupt(self, monkeypatch):
        monkeypatch.setattr(
            "builtins.input",
            lambda: (_ for _ in ()).throw(KeyboardInterrupt),
        )
        with pytest.raises(SystemExit) as exc_info:
            collect_answers()
        assert exc_info.value.code == 130


class TestHatchMain:
    def test_hatch_main_runs_wizard_when_no_args(self, monkeypatch):
        import pathlib, sys as _sys
        _hp = pathlib.Path(__file__).parent.parent
        if str(_hp) not in _sys.path:
            _sys.path.insert(0, str(_hp))
        from src import hatch
        monkeypatch.setattr(_sys, "argv", ["hatch.py"])
        inputs = iter(["my-proj", "1", ".", "85", "n"])
        monkeypatch.setattr("builtins.input", lambda: next(inputs))
        called = []
        monkeypatch.setattr(hatch, "scaffold", lambda *args, **kw: called.append(kw))
        hatch.main()
        assert len(called) == 1
        assert called[0]["project_name"] == "my-proj"

    def test_hatch_main_forwards_cli_flags_to_wizard(self, monkeypatch, capsys):
        import pathlib, sys as _sys
        _hp = pathlib.Path(__file__).parent.parent
        if str(_hp) not in _sys.path:
            _sys.path.insert(0, str(_hp))
        from src import hatch
        monkeypatch.setattr(
            _sys, "argv",
            ["hatch.py", "my-cli-proj", "--template", "web", "--coverage", "95"],
        )
        called_with = []
        monkeypatch.setattr(hatch, "scaffold", lambda *args, **kwargs: called_with.append(kwargs))
        hatch.main()
        assert len(called_with) == 1
        assert called_with[0]["project_name"] == "my-cli-proj"
        assert called_with[0]["template"] == "web"
        assert called_with[0]["coverage_threshold"] == 95

    def test_cli_coverage_threshold_is_used_in_scaffold(self, monkeypatch):
        import pathlib, sys as _sys
        _hp = pathlib.Path(__file__).parent.parent
        if str(_hp) not in _sys.path:
            _sys.path.insert(0, str(_hp))
        from src import hatch
        monkeypatch.setattr(
            _sys, "argv",
            ["hatch.py", "proj", "--coverage", "75"],
        )
        called = []
        monkeypatch.setattr(hatch, "scaffold", lambda *args, **kw: called.append(kw))
        hatch.main()
        assert called[0]["coverage_threshold"] == 75

    def test_scaffold_uses_coverage_threshold_in_workflow(self, monkeypatch):
        import pathlib, sys as _sys
        _hp = pathlib.Path(__file__).parent.parent
        if str(_hp) not in _sys.path:
            _sys.path.insert(0, str(_hp))
        from src import hatch
        monkeypatch.setattr(
            _sys, "argv",
            ["hatch.py", "proj", "--coverage", "92"],
        )
        called = []
        monkeypatch.setattr(hatch, "scaffold", lambda *args, **kw: called.append(kw))
        hatch.main()
        assert called[0]["coverage_threshold"] == 92

    def test_scaffold_defaults_to_85_coverage_threshold(self, monkeypatch):
        import pathlib, sys as _sys
        _hp = pathlib.Path(__file__).parent.parent
        if str(_hp) not in _sys.path:
            _sys.path.insert(0, str(_hp))
        from src import hatch
        monkeypatch.setattr(_sys, "argv", ["hatch.py", "proj"])
        called = []
        monkeypatch.setattr(hatch, "scaffold", lambda *args, **kw: called.append(kw))
        hatch.main()
        assert called[0]["coverage_threshold"] == 85

from src.utils.wizard import (run_wizard)


def test_ask_handles_eof_as_empty_input_and_returns_default(monkeypatch):
    """Line 93: EOFError on input() during ask() is treated as empty
    input, falling back to the default rather than crashing."""
    def raise_eof():
        raise EOFError
    monkeypatch.setattr("builtins.input", raise_eof)
    result = ask("Name", default="fallback-name")
    assert result == "fallback-name"


def test_choose_handles_eof_as_empty_input_and_returns_default(monkeypatch):
    """Lines 129-130: EOFError on input() during choose() falls back to
    the default selection."""
    def raise_eof():
        raise EOFError
    monkeypatch.setattr("builtins.input", raise_eof)
    result = choose("Pick", TEMPLATE_CHOICES, default="web")
    assert result == "web"


def test_yes_no_handles_eof_as_empty_input_and_returns_default(monkeypatch):
    """Lines 147-148: EOFError on input() during yes_no() falls back to
    the default boolean."""
    def raise_eof():
        raise EOFError
    monkeypatch.setattr("builtins.input", raise_eof)
    assert yes_no("Proceed?", default=True) is True
    monkeypatch.setattr("builtins.input", raise_eof)
    assert yes_no("Proceed?", default=False) is False


def test_run_wizard_returns_collect_answers_result(monkeypatch):
    """Line 214: run_wizard() is a thin wrapper around collect_answers()
    and always returns a dict."""
    from src.utils import wizard as wizard_module

    sentinel = {"project_name": "sentinel-proj"}
    monkeypatch.setattr(wizard_module, "collect_answers", lambda defaults=None: sentinel)

    result = run_wizard(defaults={"template": "lib"})
    assert result == sentinel
