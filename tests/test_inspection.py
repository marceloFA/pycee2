import pytest
from collections import defaultdict

from pycee.inspection import (
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
    source.write(
        "import collections\nimport kivy\nbar = collections.Counter()\nprint('foo')\n"
    )
    return source


@pytest.fixture()
def traceback_fixture(source_file_fixture):
    """ make text content of traceback easily available """
    return get_traceback_from_script(str(source_file_fixture))


def test_get_traceback_from_script(source_file_fixture):

    path = str(source_file_fixture)
    expected_traceback_content = f"Traceback (most recent call last):\n  File \"{path}\", line 2, in <module>\n    import kivy\nModuleNotFoundError: No module named 'kivy'\n"
    assert get_traceback_from_script(path) == expected_traceback_content


def test_get_error_message(traceback_fixture):

    error_message = get_error_message(traceback_fixture)
    assert error_message == "ModuleNotFoundError: No module named 'kivy'"


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

    error_message = "from collections import Counter\nimport kivy\nfrom stats import median as stats_median\n"
    packages = defaultdict(
        list,
        {
            "import_name": ["collections", "kivy", "stats"],
            "import_from": ["Counter", "median"],
        },
    )

    assert get_packages(error_message) == packages
