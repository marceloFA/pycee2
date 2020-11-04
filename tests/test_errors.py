import pytest

from pycee.errors import (
    handle_key_error
)

from pycee.utils import ERROR_MESSAGES

@pytest.mark.parametrize(
    'error_message, offending_line, expected',
    [
        ("KeyError: 1", "a_dict[1]", "Dictionary 'a_dict' does not have a key with value 1."),
        ("KeyError: 1", "a_dict[1] + a_dict[2]", "Dictionary 'a_dict' does not have a key with value 1."),
        ("KeyError: 'foo'", "a_dict['foo']", "Dictionary 'a_dict' does not have a key with value 'foo'."),
        ("KeyError: 'foo'", "a_dict['foo'] + a_dict['bar']", "Dictionary 'a_dict' does not have a key with value 'foo'."),
        ("KeyError: ('foo',)", "a_dict[('foo',)]", "Dictionary 'a_dict' does not have a key with value ('foo',)."),
        ("KeyError: ('foo',)", "a_dict[('foo',)] + a_dict[('bar',)]", "Dictionary 'a_dict' does not have a key with value ('foo',)."),
        ("KeyError: (1,2)", "a_dict[(1,2)]", "Dictionary 'a_dict' does not have a key with value (1,2)."),
        ("KeyError: (1,2)", "a_dict[(1,2)] a_dict[(3,4)]", "Dictionary 'a_dict' does not have a key with value (1,2)."),
    ]
)
def test_handle_key_error_with_known_target(error_message, offending_line, expected, monkeypatch):
    monkeypatch.setitem(ERROR_MESSAGES, "KeyError", "<initial_error>")
    assert handle_key_error(error_message, offending_line) == expected


@pytest.mark.parametrize(
    'error_message, offending_line, expected',
    [
        ("KeyError: 1", "a[1], b[1]", "One of dictionaries a, b does not have a key with value 1."),
        ("KeyError: 'foo'", "a['foo'], b['foo']", "One of dictionaries a, b does not have a key with value 'foo'."),
        ("KeyError: ('foo',)", "a[('foo',)], b[('foo'),]", "One of dictionaries a, b does not have a key with value ('foo',)."),
        ("KeyError: (1,2)", "a[(1,2)] b[(1,2)]", "One of dictionaries a, b does not have a key with value (1,2)."),
    ]
)
def test_handle_key_error_with_unknown_target(error_message, offending_line, expected, monkeypatch):
    monkeypatch.setitem(ERROR_MESSAGES, "KeyError", "<initial_error>")
    assert handle_key_error(error_message, offending_line) == expected