import pytest
from collections import defaultdict

from pycee.inspection import (
    get_error_info,
    get_traceback_from_script,
    get_error_message,
    get_error_type,
    get_error_line,
    get_file_name,
    get_code,
    get_offending_line,
)


# TODO: should these fixtures have scopes?
@pytest.fixture()
def source_file_fixture(tmpdir):
    """ Simulate a file that contains python code that generates an error """
    source = tmpdir.join("error_code.py")
    source.write("import collections\nimport not_a_module\nbar = collections.Counter()\nprint('foo')\n")
    return source


@pytest.fixture()
def errorless_file_fixture(tmpdir):
    """ Simulate a file that contains python code without errors """
    source = tmpdir.join("errorless_code.py")
    source.write("print('This code should execute flawlessly')")
    return source


@pytest.fixture()
def traceback_fixture(source_file_fixture):
    """ make text content of traceback easily available """
    return get_traceback_from_script(str(source_file_fixture))


def test_get_error_info_exit_with_code_0_if_no_error(errorless_file_fixture, capsys):

    with pytest.raises(SystemExit) as e:
        get_error_info(str(errorless_file_fixture))
        out, err = capsys.readouterr()
        assert e.value.code == 0
        # assert we haven't left tthe user with a empty output
        # The actual message may change so it content doesn't really matter
        assert out


def test_get_traceback_from_script_captures_error(source_file_fixture):

    path = str(source_file_fixture)
    expected_traceback_content = f"Traceback (most recent call last):\n  File \"{path}\", line 2, in <module>\n    import not_a_module\nModuleNotFoundError: No module named 'not_a_module'\n"
    assert get_traceback_from_script(path) == expected_traceback_content


def test_get_traceback_from_script_return_none_if_no_error(errorless_file_fixture):

    expected = None
    assert get_traceback_from_script(str(errorless_file_fixture)) == expected


def test_get_error_message(traceback_fixture):

    error_message = get_error_message(traceback_fixture)
    assert error_message == "ModuleNotFoundError: No module named 'not_a_module'"


def test_get_error_type(traceback_fixture):

    error_message = get_error_message(traceback_fixture)
    error_type = get_error_type(error_message)
    assert error_type == "ModuleNotFoundError"


def test_get_error_line(traceback_fixture):

    error_line = get_error_line(traceback_fixture)
    assert error_line == 2


def test_get_file_name(source_file_fixture, traceback_fixture):

    file_name = get_file_name(traceback_fixture)
    assert file_name == str(source_file_fixture)


def test_get_code(source_file_fixture):

    assert get_code(str(source_file_fixture)) == source_file_fixture.read()


def test_get_offending_line_module_error(traceback_fixture, source_file_fixture):

    error_line = get_error_line(traceback_fixture)
    print(error_line)
    code = get_code(str(source_file_fixture))
    offending_line = get_offending_line(error_line, code)
    assert offending_line == "import not_a_module"


def test_get_offending_line_attr_error():
    error_line = 8
    code = "import os\nimport math\n\n\nprint(os.getcwd())\nprint(math.pi)\nmath.dir\n"
    offending_line = get_offending_line(error_line, code)
    assert offending_line == "math.dir"


def test_get_offending_line_type_error():
    error_line = 9
    code = "import os\nimport math\n\n\nprint(os.getcwd())\nprint(math.pi)\n\n# will raise an typeerror\nmath.pi + 'not an int'\n\n\n\n# just for testing purposes\n\n\n"
    offending_line = get_offending_line(error_line, code)
    assert offending_line == "math.pi + 'not an int'"


def test_get_offending_line_syntax_error_EOL_literal():
    error_line = 10
    code = "import os\nimport math\n\n\nprint(os.getcwd())\nprint(math.pi)\n\n# will raise an syntax error\n\nprint('error)\n\n\n# just for testing purposes\n\n\n"
    offending_line = get_offending_line(error_line, code)
    assert offending_line == "print('error)"


def test_get_offending_line_syntax_error_generic():
    error_line = 8
    code = "import os\nimport math\n\n\nprint(os.getcwd())\nprint(math.pi)\n\ndef foo(bar)\n    pass\n\n# just for testing purposes\n\n\n"
    offending_line = get_offending_line(error_line, code)
    assert offending_line == "def foo(bar)"
