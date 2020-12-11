import pytest

from pycee.errors import handle_module_error_locally
from pycee.utils import HINT_MESSAGES


def test_module_not_found_error_locally(monkeypatch):
    monkeypatch.setitem(HINT_MESSAGES, "ModuleNotFoundError", "<missing_module>")
    error_message = "ModuleNotFoundError: No module named 'sklearn'"
    assert handle_module_error_locally(error_message) == "sklearn"
