import pytest

from pycee.errors import handle_name_error_locally
from pycee.utils import HINT_MESSAGES


def test_module_not_found_error_locally(monkeypatch):
    monkeypatch.setitem(HINT_MESSAGES, "NameError", "<missing_name>")
    error_message = "NameError: name 'some_variable' is not defined"
    assert handle_name_error_locally(error_message) == "some_variable"
