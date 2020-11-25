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
    get_packages,
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


def test_get_code(source_file_fixture, traceback_fixture):

    assert get_code(str(source_file_fixture)) == source_file_fixture.read()


def test_get_packages():

    error_message = "from collections import Counter\nimport not_a_module\nfrom stats import median as stats_median\n"
    packages = defaultdict(
        list,
        {
            "import_name": ["collections", "not_a_module", "stats"],
            "import_from": ["Counter", "median"],
        },
    )

    assert get_packages(error_message) == packages