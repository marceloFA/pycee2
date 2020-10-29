""" Contains all the logic that handles code errors """
import re
import sys
from json import load
from os.path import join
from typing import List, Union
from keyword import kwlist

from difflib import get_close_matches
from slugify import slugify

from .utils import get_project_root, DATA_TYPES, BUILTINS
from .utils import (
    SINGLE_QUOTE_CHAR,
    DOUBLE_QUOTE_CHAR,
    SINGLE_SPACE_CHAR,
    EMPTY_STRING,
)

# Stack Overflow URL for scraping
API_SEARCH_URL = "https://api.stackexchange.com/2.2/search?site=stackoverflow"


def determine_query(error_info: dict, offending_line: int, packages) -> str:
    """ choose the correct query to run based on the error type """

    pydoc_info = None
    error_type = error_info["type"]
    error_message = error_info["message"]
    traceback = error_info["traceback"]

    if error_type == "SyntaxError":
        query = handle_syntax_error(error_message, offending_line)

    elif error_type == "TabError":
        query = handle_tab_error(error_message)

    elif error_type == "IndentationError":
        query = handle_indentation_error(error_message)

    elif error_type == "IndexError":
        query = handle_index_error(error_message)

    elif error_type == "AttributeError":
        query = handle_attr_error(error_message)
        search = convert(extract_quoted_words(traceback))[1]
        if search:
            pydoc_info = get_help(search, packages, DATA_TYPES)

    elif error_type == "KeyError":
        query = handle_key_error(error_message)

    elif error_type == "NameError":
        query = handle_name_error(error_message)
        search = convert(extract_quoted_words(traceback))[0]
        if search:
            pydoc_info = get_help(search, packages, DATA_TYPES)

    else:
        query = url_for_error(error_message)  # default query

    return query, pydoc_info


def handle_key_error(error_message: str) -> str:
    """ refactor this, please """

    # check for quotation marks which will contain code specific data for specific error
    while SINGLE_QUOTE_CHAR in error_message:
        start = error_message.find(SINGLE_QUOTE_CHAR)
        end = error_message[start + 1 :].find(SINGLE_QUOTE_CHAR) + start + 2
        error_message = error_message.replace(error_message[start:end], EMPTY_STRING)

    while DOUBLE_QUOTE_CHAR in error_message:
        start = error_message.find(DOUBLE_QUOTE_CHAR)
        end = error_message[start + 1 :].find(DOUBLE_QUOTE_CHAR) + start + 2
        error_message = error_message.replace(error_message[start:end], EMPTY_STRING)

    return url_for_error(error_message)


def handle_attr_error(error_message):
    """ docstring later on """

    quoted_words = convert(extract_quoted_words(error_message))
    error = " ".join(quoted_words)
    error = slugify(error, separator="+")
    return url_for_error(error)


def handle_indentation_error(error_message):
    """ Process an IndentationError """
    message = remove_exception_from_error_message(error_message)
    return url_for_error(message)


def handle_index_error(message):
    """ docstring later on """

    to_remove = " cannot be "
    if to_remove in error:
        error = message.replace(to_remove, EMPTY_STRING)

    error = message.replace("IndexError:", "index error")
    error = slugify(message, separator="+")

    return url_for_error(error)


def handle_name_error(message):
    """ docstring later on """

    variables = []
    query = ""

    if SINGLE_QUOTE_CHAR in message:

        variables = convert(extract_quoted_words(message))
        to_add = None

        if len(variables) > 1:
            to_add = get_action_word(variables[0], variables[1])
        else:
            to_add = get_action_word(variables[0])

        if not to_add:
            return url_for_error("NameError")

        query = query + to_add + " to " + variables[0]
        return url_for_error(query)

    # generic name error search
    else:
        return url_for_error("NameError")


def handle_syntax_error(offending_line):
    """ docstring later on """

    # unmathcing number of quotation marks error
    single = offending_line.count(SINGLE_QUOTE_CHAR)
    double = offending_line.count(DOUBLE_QUOTE_CHAR)

    if (single + double) % 2 == 1:
        return url_for_error("quotation marks")

    # unmathcing number of parenthese, brackets or braces error
    opening_brackets = (
        offending_line.count("(")
        + offending_line.count("[")
        + offending_line.count("{")
    )
    closing_bracket = (
        offending_line.count(")")
        + offending_line.count("]")
        + offending_line.count("}")
    )

    if opening_brackets != closing_bracket:
        return url_for_error("bracket meanings")

    # split offendingline and remove symbols
    # what does this matches?
    regex = r"[!@#$%^&*_\-+=\(\)\[\]\{\}\\|~`/?.,<>:; ]"
    tokens = re.split(regex, offending_line)
    # remove strings/quotes
    for token in tokens:
        if (SINGLE_QUOTE_CHAR in token) or (DOUBLE_QUOTE_CHAR in token):
            tokens.remove(token)
    # then find possibilites for each word
    possibilites = []
    for token in tokens:
        possible = []
        possible.extend(get_close_matches(token.lower(), kwlist, 3, 0.6))
        possible.extend(get_close_matches(token.lower(), BUILTINS, 3, 0.6))

        # if exact match, only keep that word
        flag = False
        for word in possible:
            if word == token:
                possibilites.append(word)
                flag = True
        if not flag:
            possibilites.extend(possible)

    query = check_tokens_for_query(possibilites)
    return url_for_error(query)


def handle_tab_error(error_message):
    """ Process an TabError """
    message = remove_exception_from_error_message(error_message)
    return url_for_error(message)


def handle_type_error(error_message):
    """ Process an TypeError """

    hint1 = "the first argument must be callable"
    hint2 = "not all arguments converted during string formatting"

    if hint1 in error_message:
        return url_for_error("must have first callable argument")
    elif hint2 in message:
        message = remove_exception_from_error_message(error_message)
        return url_for_error(message)
    else:
        # generic search
        return url_for_error(error_message)


#### Helpers


def check_tokens_for_query(tokens: List) -> str:
    """  Check SyntaxError tokens to determine an apropriate query """

    if "for" in tokens:
        return "for loop"
    elif "while" in tokens:
        return "while loop"
    elif "if" in tokens or "else" in tokens:
        return "if else syntax"
    elif "def" in tokens:
        return "function definition"
    else:
        return "SyntaxError: invalid syntax"


def convert(quoted_words: List[str]) -> List[str]:
    """take some quoted words on the error message
    and try to translate then.
    """
    translated_words = [search_translate(w) for w in quoted_words]
    return translated_words


def extract_quoted_words(error_message: str) -> List[str]:
    """This method will extract words surrounded by single quotes.
    Example:
    input: "AttributeError: 'int' object has no attribute 'append'"
    output: ['int', 'append']
    """
    return error_message.split(SINGLE_QUOTE_CHAR)[1::2]


def get_query_params(error_message: str):
    """ preps the query to include necessary filters and meet URL format """

    error_message_slug = slugify(error_message, separator="+")
    order = "&order=desc"
    sort = "&sort=votes"
    python_tagged = "&tagged=python"
    intitle = f"&intitle={error_message_slug}"

    return order + sort + python_tagged + intitle


def get_action_word(search1=None, search2=None) -> Union[None]:
    """ Returns action word associated with input """

    if not search1 and not search2:
        return None

    with open(join(get_project_root(), "python_tasks.txt"), "rb") as temp_content:
        temp_content = temp_content.read().decode("utf-8", errors="ignore").split("\n")

    # action - object - preposition
    content = []
    # clean data
    i = 0
    for line in temp_content:
        content.append([])
        lst = line.split("] ")
        for item in lst:
            item = item.strip(" []\n\r")
            content[i].append(item)
        i = i + 1
    # search by two words, frequency analysis by action, additional constraints
    counter = []
    actions = []

    for line in content[1 : len(content) - 1]:
        c_1 = not search1 and search2 in line[2]
        c_2 = not search2 and search1 in line[1]
        c_4 = search1 and search2
        c_5 = search1 in line[1] and search2 in line[2]
        c_3 = c_4 and c_5

        if c_1 or c_2 or c_3:
            if line[0] not in actions:
                actions.append(line[0])
                counter.append(1)
            else:
                counter[actions.index(line[0])] = counter[actions.index(line[0])] + 1

    if not counter:
        return None

    # return the max found amongst results
    return actions[counter.index(max(counter))]


def search_translate(word: str) -> str:
    """Try to get a more readable translation of a programming term.
    Else try to look up for a translation on the syntax_across_languages file.
    If both tries fails then return the unchanged word.
    """

    # syntax from http://rigaux.org/language-study/syntax-across-languages.html#StrngCSTSSASn
    # first entry is python, rest are other langauges
    with open(join(get_project_root(), "syntax_across_languages.json"), "r") as file:
        syntax_across_languages = load(file)

    word = word.lstrip().lower()
    word = word.replace(SINGLE_QUOTE_CHAR, EMPTY_STRING)
    readable_DATA_TYPES = [
        "integer",
        "float",
        "complex",
        "boolean",
        "string",
        "bytes",
        "list",
        "tuple",
        "set",
        "dictionary",
    ]

    if word in DATA_TYPES:
        return readable_DATA_TYPES[DATA_TYPES.index(word)]

    # search through provided list
    for syntax in syntax_across_languages:
        if word in syntax:
            return syntax[0]

    # if no match, find containing
    for syntax in syntax_across_languages:
        for elm in syntax:
            if word in elm:
                return syntax[0]

    return word


def url_for_error(error_message: str) -> str:
    """ Build a valid search url """

    return API_SEARCH_URL + get_query_params(error_message)


def get_help(search, packages, datatypes):
    """ gets help from the Python help() """

    changed = False
    path = "output.txt"
    lines = help_to_list(path, search)

    if "No Python documentation found for" in lines[0]:
        lines = []
    else:
        lines = help_to_code(search, lines)

    if not lines:
        for pckg_name in packages:
            try:
                pckg = importlib.import_module(pckg_name)
                search_query = pckg.__name__ + "." + search
                lines = help_to_list(path, search_query)
                if not lines:
                    break
            except:
                pass

        if not lines:
            for types in datatypes:
                search_query = types + "." + search
                lines = help_to_list(path, search_query)
                if lines:
                    break
    else:
        changed = True

    if not changed and lines:
        if "No Python documentation found for" in lines[0]:
            lines = []
        else:
            lines = help_to_code(search, lines)

    return lines


def help_to_list(path, search):
    """ Converts the help() format to an easy to use list """

    with open(path, "w") as file:
        sys.__stdout__ = sys.stdout
        sys.stdout = file
        help(search)

    sys.stdout = sys.__stdout__

    with open(path) as file2:
        lines = file2.read().splitlines()

    return lines if lines else None


def help_to_code(search, lines):
    """ Extracts the code from a list of help() data """
    res = []

    if len(lines) <= 2:
        return res

    if "class " + search in lines[2]:
        i = 3
        while lines[i].strip(" |"):
            res.append(lines[i].strip(" |"))
            i += 1

    elif search + " = " in lines[2]:
        res.append(lines[3].strip(" |"))

    if len(res) and not res[0]:
        del res[0]

    return res


def remove_exception_from_error_message(error_message: str) -> str:
    """Removes the exception error from the error message.
    Example:
    input: "AttributeError: 'int' object has no attribute 'append'"
    output: "'int' object has no attribute 'append'"
    """
    return error_message.split(SINGLE_SPACE_CHAR, 1)[1]
