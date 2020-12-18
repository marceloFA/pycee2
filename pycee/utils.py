"""Some data to be kept apart from application logic."""
import argparse
from collections import namedtuple
import glob
import os
import pathlib
import sys

from consolemd import Renderer
from filecache import filecache


def parse_args(args=sys.argv[1:]):
    """A simple argparser to be used when pycee is executed as a script."""

    parser = argparse.ArgumentParser("pycee2", description="Pycee is a tool to provide user friendly error messages.")
    parser.add_argument(
        "file_name",
        type=str,
        help="Path to the script that contains the error",
    )
    parser.add_argument(
        "-q",
        metavar="--n-questions",
        type=int,
        choices=range(1, 6),
        default=3,
        dest="n_questions",
        help="Number of questions to retrieve from Stackoverflow",
    )
    parser.add_argument(
        "-a",
        metavar="--n-answers",
        type=int,
        choices=range(1, 5),
        default=3,
        dest="n_answers",
        help="Number of answers to display",
    )
    parser.add_argument(
        "-g",
        "--from-google-search",
        dest="google_search_only",
        action="store_true",
        default=False,
        help="Retrieve questions only from Google search engine",
    )
    parser.add_argument(
        "-s",
        "--stackoverflow-answer",
        dest="show_pycee_hint",
        action="store_false",
        default=True,
        help="Output only StackOverflow answers for the error",
    )
    parser.add_argument(
        "-p",
        "--pycee-hint",
        dest="show_so_answer",
        action="store_false",
        default=True,
        help="Output only pycee hint for the error",
    )
    parser.add_argument(
        "-d",
        "--dry-run",
        dest="dry_run",
        action="store_true",
        help="Return only the stackoverflow query. For test purposes",
    )
    parser.add_argument(
        "-rm",
        "--remove-cache",
        dest="rm_cache",
        action="store_true",
        default=False,
        help="Remove all local cache files",
    )
    parser.add_argument(
        "-f",
        "--no-cache",
        dest="cache",
        action="store_false",
        default=True,
        help="Force API requests by skipping any local caches",
    )

    return parser.parse_args(args)


def remove_cache():
    """Util to remove the cache files, which can be located at two different places
    depending if pycee is running as a installed pacakge or as a cloned repository"""

    installed_module_path = pathlib.Path(__file__).parent.absolute()
    package_cache = glob.glob(os.path.join(installed_module_path, "*.cache*"))
    local_cache = glob.glob("pycee/*.cache*")
    files = package_cache + local_cache
    print("Cache removed!\nPlease run pycee again without -rm or --remove-cache argument to get your answers")
    # excecvp replace the curent process
    # This is currently necessary because filecache package
    # wouldn't let me delete all cache files on the main process
    # -f so not found files won't polute the terminal
    os.execvp("rm", ["rm", "-f"] + files)
    # after execv vp finishes executing rm it exites


def print_answers(so_answers, pycee_hint, pydoc_answer, args):
    """ Hide the logic of printing answers from the usage example """

    if args.show_so_answer:

        if not so_answers:
            print("\nPycee couldn't find answers for the error on Stackoverflow.")
        else:
            renderer = Renderer()
            for i, answer in enumerate(so_answers):
                print(f"\nSolution {i}:")
                renderer.render(answer)

    if args.show_pycee_hint:
        if not pycee_hint:
            print("\nPycee does not have an hint for fixing this error on its manuals.")
        else:
            print("\nPycee Answer:")
            print(pycee_hint)


# These are some constants we use throughout the codebase
DEFAULT_HTML_PARSER = "html5lib"
SINGLE_QUOTE_CHAR = "'"
DOUBLE_QUOTE_CHAR = '"'
SINGLE_SPACE_CHAR = " "
EMPTY_STRING = ""
COMMA_CHAR = ","

BASE_URL = "https://api.stackexchange.com/2.2"
SEARCH_URL = BASE_URL + "/search?site=stackoverflow"
ANSWERS_URL = BASE_URL + "/questions/<id>/answers?site=stackoverflow&filter=withbody"

# A list of all standard exeptions
BUILTINS = dir(sys.modules["builtins"])

# namedtuples to represent simple objects
Question = namedtuple("Question", ["id", "has_accepted"])
Answer = namedtuple("Answer", ["id", "accepted", "score", "body", "author", "profile_image"])
HINT_MESSAGES = {
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
    "IndexError": (
        "You tried to acess an index that does not exist in a <sequence> at line <line>."
        "\nAn IndexError happens when asking for non existing indexes values of sequences."
        "\nSequences can be lists, tuples and range objects."
        "\nTo fix this make sure that the index value is valid."
    ),
    "SyntaxError": (
        "You have a syntax error somewehre arround line <line>"
        "\nGenerally, syntax errors occurs when multiple code statements are interpreted as if they were one."
        "\nThis may be caused by several simple issues, below is a list of them."
        "\nYou should check if your code contains any of these issues."
        "\n"
        "\n1- Make sure that any strings in the code have matching quotation marks."
        "\n2- An unclosed bracket – (, {, or [ – makes Python continue with the next line as part of the current statement."
        "\n   Generally, an error occurs almost immediately in the next line."
        "\n3- Make sure you are not using a Python keyword for a variable name."
        "\n4- Check that you have a colon at the end of the header of every compound statement,"
        "\n   including for, while, if, and def statements."
        "\n5- Check for the classic '=' instead of '==' in a conditional statement."
        "\nSource: https://www.openbookproject.net/thinkcs/python/english2e/app_a.html"
    ),
}

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
