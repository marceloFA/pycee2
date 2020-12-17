"""This module will build the sym table for the error source code."""
from typing import List
import re

from symtable import symtable


def trim_and_split_code(code: str, error_line: str) -> List[str]:
    """This will trimm all code that comes after the line
    that contains the error and return the code that remains
    splitted in separated lines.
    """
    code = code.split("\n")
    trimmed_code = ""

    if error_line > 0:
        trimmed_code = code[:error_line]
    else:
        trimmed_code = code[0]

    return trimmed_code

def get_syntax_error_skipable_lines(traceback):
    """SyntaxError has as aditional line to exactly where the error is.
    And this makes the traceback different from other errors.
    This method will return the number of uninformative lines
    we can skip from a SyntaxError.
    """
    if "^" not in traceback:
        # accept compiler line
        return 1

    lines = traceback.split("\n")
    del lines[3]  # remove inital error message
    del lines[0]  # remove final error message

    # set max length, if first token ends at the same position as ^
    # then the error is on the previous line
    max_length = len(lines[1].split("^")[0]) + 1
    tmp = re.split(r"[!@#$%^&*_\-+=\(\)\[\]\{\}\\|~`/?.,<>:; ]", lines[0])

    i = 0
    while not tmp[i]:
        i += 1
    temp_len = i + len(tmp[i])
    # take previous line
    if temp_len >= max_length:
        return 2
