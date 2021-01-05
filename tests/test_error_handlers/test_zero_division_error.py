import pytest
from pycee import errors
from pycee.utils import HINT_MESSAGES


def test_handle_zero_division_error():
    assert (
        errors.handle_zero_division_error("ZeroDivisionError: division by zero")
        == "https://api.stackexchange.com/2.2/search?site=stackoverflow&order=desc&sort=relevance&tagged=python&intitle=division+by+zero"
    )


def test_handle_zero_division_error_locally(monkeypatch):
    monkeypatch.setitem(HINT_MESSAGES, "ZeroDivisionError", "<line>")
    assert errors.handle_zero_division_error_locally(error_line=5) == "5"
