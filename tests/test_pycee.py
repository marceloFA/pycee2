from pycee.error_info import (
    get_compilation_error_from_file,
    get_error_message,
    get_error_type,
    get_error_line,
    get_file_name,
    get_code

)

# TODO: add error_message fixture. So it'll dry out repetitions

def test_get_compilation_error_from_file():
    expected_compilation_error = 'Traceback (most recent call last):\n  File "example_code.py", line 2, in <module>\n    import kivy\nModuleNotFoundError: No module named \'kivy\''
    compilation_error = get_compilation_error_from_file(file_name='tests/test_error_message.txt')
    assert compilation_error == expected_compilation_error

def test_get_error_message():
    traceback = get_compilation_error_from_file(file_name='tests/test_error_message.txt')
    error_message = get_error_message(traceback)
    assert error_message == 'ModuleNotFoundError: No module named \'kivy\''

def test_get_error_type():
    traceback = get_compilation_error_from_file(file_name='tests/test_error_message.txt')
    error_message = get_error_message(traceback)
    error_type = get_error_type(error_message)
    assert error_type == 'ModuleNotFoundError'

def test_get_error_line():
    error_message = get_compilation_error_from_file(file_name='tests/test_error_message.txt')
    error_line = get_error_line(error_message)
    assert error_line == 2

def test_get_file_name():
    error_message = get_compilation_error_from_file(file_name='tests/test_error_message.txt')
    file_name = get_file_name(error_message)
    assert file_name == 'example_code.py'

def test_get_code():
    code = get_code('example_code.py')
    assert code == 'import collections\nimport kivy\n'
