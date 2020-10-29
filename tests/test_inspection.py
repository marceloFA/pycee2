import pytest
from collections import defaultdict

from pycee.inspection import (
    get_compilation_error_from_file,
    get_error_message,
    get_error_type,
    get_error_line,
    get_file_name,
    get_code,
    get_packages,
)


# TODO: should these fixtures have scopes?

@pytest.fixture()
def traceback_file(tmpdir):
    """ A fixture to simulate a file that contains the traceback text of an compilation error """
    traceback = tmpdir.join('traceback.txt')
    traceback.write("Traceback (most recent call last):\n  File \"error_code.py\", line 2, in <module>\n    import kivy\nModuleNotFoundError: No module named 'kivy'")
    return traceback

@pytest.fixture()
def source_file(tmpdir):
    """ A fixture to simulate a file that contains python code that generates an error """
    source = tmpdir.join('error_code.py')
    source.write('import collections\nimport kivy\n\n\nbar = collections.Counter()\nprint(\'foo\')')
    return source


def test_get_compilation_error_from_file(traceback_file):
    actual_comp_error = get_compilation_error_from_file(file_name=str(traceback_file))
    assert traceback_file.read() == actual_comp_error


def test_get_error_message(traceback_file):
    traceback = get_compilation_error_from_file(file_name=str(traceback_file))
    error_message = get_error_message(traceback)
    assert error_message == "ModuleNotFoundError: No module named 'kivy'"


def test_get_error_type(traceback_file):
    traceback = get_compilation_error_from_file(file_name=str(traceback_file))
    error_message = get_error_message(traceback)
    error_type = get_error_type(error_message)
    assert error_type == "ModuleNotFoundError"


def test_get_error_line(traceback_file):
    error_message = get_compilation_error_from_file(file_name=str(traceback_file))
    error_line = get_error_line(error_message)
    assert error_line == 2


def test_get_file_name(traceback_file):
    error_message = get_compilation_error_from_file(file_name=str(traceback_file))
    file_name = get_file_name(error_message)
    assert file_name == "error_code.py"


def test_get_code(source_file):
    assert get_code(str(source_file)) == source_file.read()


def test_get_packages():
    error_message = 'from collections import Counter\nimport kivy\nfrom stats import median as stats_median\n'
    packages = defaultdict(list,{'import_name': ['collections', 'kivy', 'stats'],'import_from': ['Counter', 'median']})
    
    assert get_packages(error_message) == packages
    