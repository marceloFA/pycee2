import pytest
from pycee import errors
from pycee import utils


def test_syntax_error_locally_with_generic_error(monkeypatch):
    monkeypatch.setitem(utils.HINT_MESSAGES, "SyntaxError", "<line>")
    assert errors.handle_syntax_error_locally(error_message="SyntaxError: invalid syntax", error_line=123) == "123"
    assert errors.handle_syntax_error_locally("SyntaxError: unexpected EOF while parsing", error_line=123) == None


def test_syntax_error_locally_with_known_error(monkeypatch):
    def mock_url(error):
        return "base_url:" + error

    monkeypatch.setattr(errors, "url_for_error", mock_url)
    assert (
        errors.handle_syntax_error(error_message="SyntaxError: unexpected EOF while parsing")
        == "base_url:syntaxerror+unexpected+eof+while+parsing"
    )
    assert errors.handle_syntax_error(error_message="SyntaxError: invalid syntax") == None
