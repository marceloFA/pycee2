""" This module will inspect the error source code and the error log."""
import os
import re
import sys
from dis import get_instructions
from collections import defaultdict
from typing import Union

from .utils import BUILTINS, EMPTY_STRING
from .utils import get_project_root

project_root = get_project_root()


def get_compilation_error_from_file(file_name: str = "example_error_msg.txt") -> str:
    """If we're integrating with PythonBuddy, this adapter will be replaced.
    As a mean of developing Pycee, this is enough.
    """

    with open(os.path.join(project_root, file_name), "r") as error_msg_file:
        traceback = error_msg_file.read()
    return traceback


def get_error_message(trackback: str) -> Union[str, None]:
    """Extracts the error message from the trackback.
    If no error message is found, will return None.
    Here's an example:

    input:
    Traceback (most recent call last):
    File "example_code.py", line 2, in <module>
        import kivy
    ModuleNotFoundError: No module named 'kivy'

    output:
    ModuleNotFoundError: No module named 'kivy'
    """

    error_lines = trackback.split("\n")
    return error_lines[-1]


def get_error_type(error_message: str) -> Union[str, None]:
    """Gets the type of the error message and check if it's a valid error
    else return None.
    Here's an example:

    input:
        ModuleNotFoundError: No module named 'kivy'
    output:
        'ModuleNotFoundError'
    """
    error_type = error_message.split(":")[0]
    return error_type if error_type in BUILTINS else None


def get_error_line(error_message: str) -> Union[int, None]:
    """Gets the error line from the compilation message
    Here's an example:
    input:

    Traceback (most recent call last):
    File "example_code.py", line 2, in <module>
        import kivy
    ModuleNotFoundError: No module named 'kivy'

    output:
    2  # <class 'int'>
    """

    # This will match a line like this
    # 'File "foo.py", line 666'
    regex1 = r'File "(.)*", line\s(\d)*'
    # This will match a undefinite number of digits
    # at the end of a string (the error line)
    regex2 = r"([0-9])*$"

    try:
        error_header = re.search(regex1, error_message)[0]
        error_line = re.search(regex2, error_header)[0]
        return int(error_line)
    except:
        return None


def get_file_name(error_message: str) -> Union[int, None]:
    """Get the file name where the error originates'
    Here's an example:

    input:
    'File "example_code.py", line 1
        print(
            ^
    SyntaxError: unexpected EOF while parsing'

    output:
    'example_code.py'
    """
    # This will match a line like this
    # 'File "foo.py", line 666'
    regex1 = r'File "(.)*", line\s(\d)*'
    # This will match text between double quotes (file name)
    regex2 = r'"(.)*"'

    try:
        error_header = re.search(regex1, error_message)[0]
        file_name = re.search(regex2, error_header)[0]
        return file_name[1:-1]  # remove double quotes
    except:
        return None


def get_code(file_name: str) -> str:
    """ Gets the source code of the specified file """
    with open(os.path.join(project_root, file_name), "r") as file:
        code = file.read()
        return code


def get_error_info():
    """ summarize all error information we have available """
    traceback = get_compilation_error_from_file()
    error_message = get_error_message(traceback)
    error_type = get_error_type(error_message)
    error_line = get_error_line(traceback)
    file_name = get_file_name(traceback)
    code = get_code(file_name)

    error_info = {
        "traceback": traceback,
        "message": error_message,
        "type": error_type,
        "line": error_line,
        "file": file_name,
        "code": code,
    }

    if not all(error_info.values()):
        print("Aborting. Some data about the error is missing:")
        print(error_info)
        sys.exit(-1)

    return error_info


def get_packages(code: str) -> defaultdict:
    """Extracts the packages that were included in the file being inspected.
    Source for this code: https://stackoverflow.com/questions/2572582/
    Example:

    input:
    'from collections import Counter\n
     import kivy\n
     from stats import median as stats_median\n'

    output:
    defaultdict(<class 'list'>,
                {'import_name': ['collections', 'kivy', 'stats'],
                 'import_from': ['Counter', 'median']}
                )
    """

    instructions = get_instructions(code)
    import_instructions = [i for i in instructions if "IMPORT" in i.opname]
    imports = defaultdict(list)
    for instr in import_instructions:
        imports[instr.opname.lower()].append(instr.argval)

    return imports
