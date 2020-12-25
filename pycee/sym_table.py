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
