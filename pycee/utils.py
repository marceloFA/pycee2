"""Some data to be kept apart from application logic."""
import argparse
from os import path, remove
import glob
from sys import modules, argv
from collections import namedtuple

from filecache import filecache


def parse_args(args=argv[1:]):
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
        help="The number of questions to retrieve from Stackoverflow",
    )
    parser.add_argument(
        "-a",
        metavar="--n-answers",
        type=int,
        choices=range(1, 5),
        default=3,
        dest="n_answers",
        help="The number of answers to display",
    )
    parser.add_argument(
        "-s",
        "--stackoverflow-answer",
        dest="show_pycee_answer",
        action="store_false",
        default=True,
        help="Get answers only from Stackoverflow",
    )
    parser.add_argument(
        "-p",
        "--pycee-answer",
        dest="show_so_answer",
        action="store_false",
        default=True,
        help="Get answers only from from pycee",
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
    """Util to remove the cache files """

    # the location of file depend on whether using it as pip installed package or not
    files = glob.glob("*.cache*") + glob.glob("pycee/*.cache*")

    for file in files:
        try:
            remove(file)
            print(f"Removed {file}")
        except OSError as e:
            print("Error: %s : %s" % (file, e.strerror))

    print("Cache removed!\nPlease run pycee again without --remove-cache argument to get your answers")
    exit()


def print_answers(so_answers, pycee_answer, pydoc_answer, args):
    """ Hide the logic of printing answers from the usage example """

    if args.show_so_answer:

        if not so_answers:
            print("Pycee couldn't find answers for the error on Stackoverflow.")
        else:
            for i, answer in enumerate(so_answers):
                print(f"Solution {i}:")
                print(answer)

    if args.show_pycee_answer:
        print("\n\nPycee Answer:")
        print(pycee_answer)


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

# A list of all standard exeptions
BUILTINS = dir(modules["builtins"])

# namedtuples to represent simple objects
Question = namedtuple("Question", ["id", "has_accepted"])
Answer = namedtuple("Answer", ["id", "accepted", "score", "body"])

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
