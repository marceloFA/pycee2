""" Some data to be kept apart from application logic"""
import argparse
from sys import modules
from pathlib import Path
from os import path


def get_project_root() -> Path:
    """This will always return the project root, wherever it's called
    So it's safe to import this to any other file of the project.
    """
    return Path(__file__).parent.parent


def create_argparser():
    """ A simple argparser to be used when pycee is executed as a script"""

    parser = argparse.ArgumentParser("pycee2", description="easier error messages")
    parser.add_argument(
        "-f",
        metavar="--file",
        nargs="?",
        type=str,
        default=path.join(get_project_root(), "example_code.py"),
        dest="file",
        help="path to the script that contains the error",
    )
    parser.add_argument(
        "-a",
        metavar="--n-answers",
        nargs="?",
        default=3,
        type=int,
        dest="n_answers",
        help="the number of answers to retrieve from Stackoverflow",
    )
    parser.add_argument("--dry-run", dest="dry_run", action="store_true")

    return parser


# These are some constants we use throughout the codebase
DEFAULT_HTML_PARSER = "html5lib"
SINGLE_QUOTE_CHAR = "'"
DOUBLE_QUOTE_CHAR = '"'
SINGLE_SPACE_CHAR = " "
EMPTY_STRING = ""
COMMA_CHAR = ","

BASE_URL = "https://api.stackexchange.com/2.2"


ANSWER_URL = BASE_URL + "/answers/<id>?site=stackoverflow&filter=withbody"

QUESTION_ANSWERS_URL = BASE_URL + "/questions/<id>/answers?site=stackoverflow&filter=withbody"

# standard python3 datatypes
DATA_TYPES = [
    "int",
    "float",
    "complex",
    "bool",
    "str",
    "bytes",
    "list",
    "tuple",
    "set",
    "dict",
]

# A list of all standard exeptions
BUILTINS = dir(modules["builtins"])


ERROR_MESSAGES = {
    "KeyError": (
        "<initial_error>\n\nKeyError exceptions are raised to the user when a key is not found in a dictionary."
        "\nTo solve this error you may want to define a key with value <key> in the dictionary."
        "\nOr you may want to use the method .get() of a dictionary which can retrieve the value associated"
        "\nto a key even when the key is missing by passing a default value."
        "\nExample:\n\nfoo = your_dict.get('missing_key', default='bar')"
    ),
}
