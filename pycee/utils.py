"""Some data to be kept apart from application logic."""
import argparse
from sys import modules
from os import path


def create_argparser():
    """A simple argparser to be used when pycee is executed as a script."""

    parser = argparse.ArgumentParser("pycee2", description="Pycee is a tool to provide user friendly error messages.")
    parser.add_argument(
        "file_name",
        type=str,
        help="Path to the script that contains the error",
    )
    parser.add_argument(
        "-a",
        metavar="--n-answers",
        nargs="?",
        default=3,
        type=int,
        dest="n_answers",
        help="The number of answers to retrieve from Stackoverflow",
    )
    parser.add_argument(
        "-s",
        "--stackoverflow-answer",
        dest="so_answer_only",
        action="store_true",
        help="Get answers only from Stackoverflow",
    )
    parser.add_argument(
        "-p", "--pycee-answer", dest="pycee_answer_only", action="store_true", help="Get answers only from from pycee"
    )
    parser.add_argument(
        "-d",
        "--dry-run",
        dest="dry_run",
        action="store_true",
        help="Return only the stackoverflow query. For test purposes",
    )

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
    "NameError": (
        "A variable named '<missing_name>' is missing."
        "\nMaybe you forget to define this variable or even you accidentally misspelled its actual name?"
    ),
    "ModuleNotFoundError": (
        "A module (library) named '<missing_module>' is missing."
        "\nYou might want to check if this is a valid module name or"
        "\nif this module can be installed using pip like: 'pip install <missing_module>'"
    ),
}
