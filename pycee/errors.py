"""Contains all the logic that handles code errors."""
import re
from typing import List, Union
from argparse import Namespace

from slugify import slugify

from .utils import HINT_MESSAGES, SEARCH_URL
from .utils import (
    SINGLE_QUOTE_CHAR,
    SINGLE_SPACE_CHAR,
    EMPTY_STRING,
)


def handle_error(error_info: dict, cmd_args: Namespace) -> tuple:
    """Process the incoming error as needed and outputs three possible answer.
    output:
    query: an URL containing an stackoverflow query about the error.
    pycee_hint: A possible answer for the error produced locally.
    TODO: pydoc_answer: A possible answer extracted from the builtin help.
    """

    pydoc_answer = None
    pycee_hint = None
    error_type = error_info["type"]
    error_message = error_info["message"]
    error_line = error_info["line"]

    if error_type == "SyntaxError":
        pycee_hint = handle_syntax_error_locally(error_message, error_line)
        query = handle_syntax_error(error_message)

    elif error_type == "TabError":
        query = handle_tab_error(error_message)

    elif error_type == "IndentationError":
        query = handle_indentation_error(error_message)

    elif error_type == "IndexError":
        pycee_hint = handle_index_error_locally(error_message, error_line)
        query = handle_index_error(error_message)

    elif error_type == "ModuleNotFoundError":
        pycee_hint = handle_module_error_locally(error_message)
        query = handle_module_not_found_error(error_message)

    elif error_type == "TypeError":
        query = handle_type_error(error_message)

    elif error_type == "KeyError":
        pycee_hint = handle_key_error_locally(error_message, error_info["offending_line"])
        query = handle_key_error(error_message)

    elif error_type == "AttributeError":
        query = handle_attr_error(error_message)

    elif error_type == "NameError":
        pycee_hint = handle_name_error_locally(error_message)
        query = handle_name_error(error_message)

    elif error_type == "ZeroDivisionError":
        pycee_hint = handle_zero_division_error_locally(error_line)
        query = handle_zero_division_error(error_message)

    else:
        query = url_for_error(error_message)  # default query

    query = set_pagesize(query, cmd_args.n_questions) if query else None

    if cmd_args.dry_run:
        print(query)
        exit()

    return query, pycee_hint, pydoc_answer


def handle_key_error_locally(error_message: str, offending_line: str) -> str:
    """When KeyError is handled locally we remind the user that the problematic
    dict should have a key with a certain value."""

    missing_key = error_message.split(SINGLE_SPACE_CHAR, maxsplit=1)[-1]

    # this first regex will match part of the pattern of a dict acess: a_dict[some_value]
    dict_acess_regex = r"[A-Za-z_]\w*\["
    # this second regex will match only the identifier of the problematic dictionaries
    identifier_regex = r"[A-Za-z_]\w*"

    acesses = re.findall(dict_acess_regex, offending_line)
    indentifiers = [re.findall(identifier_regex, a)[0] for a in acesses]

    # when offending line deals with only the same problematic dictionary
    # we can assert a better error message
    # else when offending line contains different dictionaries with same missing key,
    # we cannot determine which dict originated the error.
    target = indentifiers[0] if len(set(indentifiers)) == 1 else None

    hint = define_hint_for_key_error_locally(target, missing_key, indentifiers)

    return hint


def handle_key_error(error_message: str) -> str:
    """ Directly asks Stackoverflow for similar errors. """

    error = slugify(error_message, separator="+")
    return url_for_error(error)


def handle_name_error_locally(error_message: str) -> str:
    """When NameError is handled locally we ask if the user
    accidentally forget to define a variable or misspelled its name."""

    missing_name = get_quoted_words(error_message)[0]
    hint = HINT_MESSAGES["NameError"].replace("<missing_name>", missing_name)
    return hint


def handle_name_error(error_message: str) -> str:
    """Process an NameError by removing the variable name.
    By doing this the default error can be search without interference
    of the variable name, which does not add to the problem.

    example:
    input:
        "NameError: name 'a' is not defined"
    output:
        "NameError: name is not defined"
    """
    return url_for_error(remove_quoted_words(error_message))


def handle_module_error_locally(error_message: str) -> str:
    """Ask if the user has passed a valid module name or
    if it's installable though pip"""

    missing_module = get_quoted_words(error_message)[0]
    hint = HINT_MESSAGES["ModuleNotFoundError"].replace("<missing_module>", missing_module)
    return hint


def handle_module_not_found_error(error_message: str) -> str:
    """Handling ModuleNoutFoundError is quite simple as most of well known packages
    already have questions on ModuleNotFoundError solved at stackoverflow"""

    message = error_message.replace("ModuleNotFoundError", EMPTY_STRING)
    return url_for_error(message)


def handle_index_error_locally(error_message: str, error_line: int) -> str:
    """Process an IndexError locally."""

    sequence = None
    if "list" in error_message:
        sequence = "list"
    elif "tuple" in error_message:
        sequence = "tuple"
    elif "range object" in error_message:
        sequence = "range object"

    hint = HINT_MESSAGES["IndexError"].replace("<sequence>", sequence)
    hint = hint.replace("<line>", str(error_line))

    return hint


def handle_index_error(message: str) -> str:
    """Process an IndexError."""

    message = slugify(message, separator="+")

    return url_for_error(message)


def handle_attr_error(error_message: str) -> str:
    """Process an AttributeError by directly asking StackOverflow
    about the error message."""

    error = slugify(error_message, separator="+")
    return url_for_error(error)


def handle_indentation_error(error_message: str) -> str:
    """Process an IndentationError."""

    message = remove_exception_from_error_message(error_message)
    return url_for_error(message)


def handle_syntax_error_locally(error_message: str, error_line: int) -> Union[str, None]:
    """ Process a SyntaxError locally """

    answer = None
    if error_message == "SyntaxError: invalid syntax":
        answer = HINT_MESSAGES["SyntaxError"].replace("<line>", str(error_line))

    return answer


def handle_syntax_error(error_message: str) -> Union[str, None]:
    """Process a SyntaxError """

    # if a generic SyntaxError happens
    # it's quite tricky to catch the right offending line
    if error_message == "SyntaxError: invalid syntax":
        return None
    else:
        error = slugify(error_message, separator="+")
        return url_for_error(error)


def handle_tab_error(error_message: str) -> str:
    """Process an TabError."""
    message = remove_exception_from_error_message(error_message)
    return url_for_error(message)


def handle_type_error(error_message: str) -> str:
    """Process an TypeError."""

    hint1 = "the first argument must be callable"
    hint2 = "not all arguments converted during string formatting"
    if hint1 in error_message:
        message = "must have first callable argument"
    elif hint2 in error_message:
        message = remove_exception_from_error_message(error_message)
    else:
        return url_for_error(error_message)

    message = slugify(message, separator="+")

    return url_for_error(message)


def handle_zero_division_error(error_message: str) -> str:
    """Process an ZeroDivisionError"""

    message = remove_exception_from_error_message(error_message)
    return url_for_error(message)


def handle_zero_division_error_locally(error_line: int) -> str:
    """Process an ZeroDivisionError"""
    hint = HINT_MESSAGES["ZeroDivisionError"].replace("<line>", str(error_line))
    return hint


# Helper methods below


def set_pagesize(query: str, pagesize: int) -> str:
    """Set the number of questions we want from Stackoverflow."""
    return query + f"&pagesize={pagesize}"


def get_query_params(error_message: str) -> str:
    """Prepares the query to include necessary filters and meet URL format."""

    error_message_slug = slugify(error_message, separator="+")
    order = "&order=desc"
    sort = "&sort=relevance"
    python_tagged = "&tagged=python"
    intitle = f"&intitle={error_message_slug}"

    return order + sort + python_tagged + intitle


def url_for_error(error_message: str) -> str:
    """Build a valid search url."""

    return SEARCH_URL + get_query_params(error_message)


def get_quoted_words(error_message: str) -> List[str]:
    """Extract words surrounded by single quotes.
    Example:
    input: "AttributeError: 'int' object has no attribute 'append'"
    output: ['int', 'append']
    """
    return error_message.split(SINGLE_QUOTE_CHAR)[1::2]


def remove_exception_from_error_message(error_message: str) -> str:
    """Removes the exception error from the error message.
    Example:
    input: "AttributeError: 'int' object has no attribute 'append'"
    output: "'int' object has no attribute 'append'"
    """
    return error_message.split(SINGLE_SPACE_CHAR, 1)[1]


def remove_quoted_words(error_message: str) -> str:
    """Removes quoted words from an error message.
    Example:
    input: "NameError: name 'a' is not defined"
    output: "NameError: name is not defined"
    """
    return re.sub(r"'.*?'\s", EMPTY_STRING, error_message)


def define_hint_for_key_error_locally(target, missing_key, indentifiers):
    hint = HINT_MESSAGES["KeyError"]
    if target:
        hint = hint.replace(
            "<initial_error>",
            f"Dictionary '{target}' does not have a key with value {missing_key}.",
        )
        hint = hint.replace("<key>", missing_key)
    else:
        formatted_identifiers = ", ".join(indentifiers)
        hint = hint.replace(
            "<initial_error>",
            f"One of dictionaries {formatted_identifiers} does not have a key with value {missing_key}.",
        )
        hint = hint.replace("<key>", missing_key)

    return hint
