from sys import modules
from pathlib import Path

# These are some constants we use throughout the codebase
DEFAULT_HTML_PARSER = "html5lib"
SINGLE_QUOTE_CHAR = "'"
DOUBLE_QUOTE_CHAR = '"'
SINGLE_SPACE_CHAR = " "
EMPTY_STRING = ""
COMMA_CHAR = ","

ANSWER_URL = (
    "https://api.stackexchange.com/2.2/answers/<id>?site=stackoverflow&filter=withbody"
)

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


def get_project_root() -> Path:
    """This will always return the project root, wherever it's called
    So it's safe to import this to any other file of the project.
    """
    return Path(__file__).parent.parent
