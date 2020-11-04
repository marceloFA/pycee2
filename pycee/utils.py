from sys import modules
from pathlib import Path


def get_project_root() -> Path:
    """This will always return the project root, wherever it's called
    So it's safe to import this to any other file of the project.
    """
    return Path(__file__).parent.parent


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
    'KeyError': """<initial_error>\n\nKeyError exceptions are raised to the user when a key is not found in a dictionary.\nTo solve this error you may want to define a key with value <key> in the dictionary.\nOr you may want to use the method .get() of a dictionary which can retrieve the value associated\nto a key even when the key is missing by passing a default value.\nExample:\n\nfoo = your_dict.get('missing_key', default='bar')""",
}
