import pytest

from pycee.errors import handle_index_error_locally
from pycee.utils import HINT_MESSAGES


@pytest.mark.parametrize(
    "error_message, error_line, sequence",
    [
        ("IndexError: list index out of range", 5, "list"),
        ("IndexError: tuple index out of range", 5, "tuple"),
        ("IndexError: range object index out of range", 5, "range object"),
    ],
)
def test_index_error_locally(error_message, error_line, sequence, monkeypatch):
    monkeypatch.setitem(HINT_MESSAGES, "IndexError", "<sequence> <line>")
    assert handle_index_error_locally(error_message, error_line) == f"{sequence} {error_line}"
