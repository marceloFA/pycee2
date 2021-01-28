import pytest

from pycee.errors import handle_index_error_locally, handle_index_error
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


@pytest.mark.parametrize(
    "error_message, result",
    [
        (
            "IndexError: list index out of range",
            "https://api.stackexchange.com/2.2/search?site=stackoverflow&order=desc&sort=relevance&tagged=python&intitle=indexerror+list+index+out+of+range",
        ),
        (
            "IndexError: tuple index out of range",
            "https://api.stackexchange.com/2.2/search?site=stackoverflow&order=desc&sort=relevance&tagged=python&intitle=indexerror+tuple+index+out+of+range",
        ),
        (
            "IndexError: range object index out of range",
            "https://api.stackexchange.com/2.2/search?site=stackoverflow&order=desc&sort=relevance&tagged=python&intitle=indexerror+range+object+index+out+of+range",
        ),
    ],
)
def test_index_error(error_message, result):
    assert handle_index_error(error_message) == result
