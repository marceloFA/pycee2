""" This module will build the sym table for the error source code """
from typing import Dict, Union, Any
from symtable import symtable
from pyminifier.minification import remove_comments_and_docstrings


def trim_and_split_code(code: str, error_line: str) -> [str]:
    """This will trimm all code that comes after the line
    that contains the error and return the code that remains
    splitted in separated lines.
    """
    code = code.split("\n")

    if error_line > 0:
        return code[:error_line]
    else:
        return code[0]


def get_offending_line(error_info):
    """ Gets the offending line. """

    offending_line = None
    is_syntax_error = error_info["type"] == "SyntaxError"
    code_lines = error_info["code"].split("\n")
    error_line = error_info["line"] - 1

    if is_syntax_error:
        uncommented_code = remove_comments_and_docstrings(error_info["code"])
        # TODO: remove this?
        # remove newline char
        uncommented_code = uncommented_code[: len(uncommented_code) - 1]
        offending_line = uncommented_code.splitlines()[-error_line]
    else:
        offending_line = code_lines[error_line]

    return offending_line


def broken_get_sym_table(error_info):
    """ This is currently broken!"""

    error_line = error_info["line"] - 1  # make this 0 indexed
    is_syntax_error = error_info["type"] == "SyntaxError"
    n_lines_to_remove = 1 if is_syntax_error else 2

    code_lines = trim_and_split_code(error_info["code"], error_line)
    clean_code = remove_comments_and_docstrings(error_info["code"])
    clean_code_lines = clean_code.split("\n")

    # adjust so we dont have to remove negtive inexistent lines
    if error_line - n_lines_to_remove <= 0:
        n_lines_to_remove = -(error_line - n_lines_to_remove) / error_line

    if is_syntax_error:
        n_lines_to_skip = get_syntax_error_skipable_lines(error_info["traceback"])
        offending_line = clean_code_lines[-n_lines_to_skip]
        n_lines_to_remove = n_lines_to_skip
    else:
        offending_line = code_lines[error_line]

    clean_code_lines = clean_code_lines[:-n_lines_to_remove]

    # get whitespace at start of line
    final = len(code_lines) - 1
    indent = code_lines[final][: -len(code_lines[final].lstrip())]

    if not clean_code_lines:
        return None

    if code_lines[final][len(code_lines[final]) - 1] == ":":
        if not indent:
            indent = "  "
        else:
            indent = indent + indent

    final_code = (
        clean_code + "\n" + indent + "import sys" + "\n" + indent + "sys.exit()" + "\n"
    )
    symTable = symtable(final_code, "userCode", "exec")
    return symTable


def get_syntax_error_skipable_lines(traceback):
    """SyntaxError has as aditional line to exactly where the error is.
    And this makes the traceback different from other errors.
    This method will return the number of uninformative lines
    we can skip from a SyntaxError.
    """
    if not "^" in traceback:
        # accept compiler line
        return 1

    lines = traceback.split("\n")
    del lines[3]  # remove inital error message
    del lines[0]  # remove final error message

    # set max length, if first token ends at the same position as ^
    # then the error is on the previous line
    maxLength = len(lines[1].split("^")[0]) + 1
    tmp = re.split(r"[!@#$%^&*_\-+=\(\)\[\]\{\}\\|~`/?.,<>:; ]", lines[0])

    i = 0
    while not tmp[i]:
        i += 1
    tempLength = i + len(tmp[i])
    # take previous line
    if tempLength >= maxLength:
        return 2
