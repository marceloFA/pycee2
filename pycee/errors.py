""" Contains all the logic that handles code errors """
import re
import sys
from json import load
from os.path import join
from keyword import kwlist
from typing import List, Union
from collections import defaultdict
from importlib import import_module
from difflib import get_close_matches

from slugify import slugify

from .utils import get_project_root, DATA_TYPES, BUILTINS, ERROR_MESSAGES
from .utils import (
    SINGLE_QUOTE_CHAR,
    DOUBLE_QUOTE_CHAR,
    SINGLE_SPACE_CHAR,
    EMPTY_STRING,
)

# Stack Overflow URL for scraping
API_SEARCH_URL = "https://api.stackexchange.com/2.2/search?site=stackoverflow"


def handle_error(
    error_info: dict, offending_line: str, packages: defaultdict, limit: int
) -> str:
    """ Process the incoming error as needed """

    query = None
    pydoc_answer = None
    pycee_answer = None
    error_type = error_info["type"]
    error_message = error_info["message"]
    traceback = error_info["traceback"]

    if error_type == "SyntaxError":
        query = handle_syntax_error(offending_line)

    elif error_type == "TabError":
        query = handle_tab_error(error_message)

    elif error_type == "IndentationError":
        query = handle_indentation_error(error_message)

    elif error_type == "IndexError":
        query = handle_index_error(error_message)

    elif error_type == "ModuleNotFoundError":
        query = handle_module_not_found_error(error_message)

    elif error_type == "KeyError":
        pycee_answer = handle_key_error(error_message, offending_line)

    elif error_type == "AttributeError":
        query = handle_attr_error(error_message)
        search = convert(get_quoted_words(traceback))[1]
        if search:
            pydoc_answer = get_help(search, packages, DATA_TYPES)

    elif error_type == "NameError":
        query = handle_name_error(error_message)
        search = None
        if search:
            pydoc_answer = get_help(search, packages, DATA_TYPES)

    else:
        query = url_for_error(error_message)  # default query

    if query:
        query = set_limit(query, limit)

    return query, pycee_answer, pydoc_answer


def set_limit(query: str, limit: int) -> str:
    """ set the number of questions (and so answers) we want"""

    limit_param = f"&pagesize={limit}"
    return query + limit_param


def handle_key_error(error_message: str, offending_line: str) -> str:
    """ KeyError is a quite simple limited error and we can handle it manually. """

    answer = ERROR_MESSAGES["KeyError"]
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

    if target:
        answer = answer.replace(
            "<initial_error>",
            f"Dictionary '{target}' does not have a key with value {missing_key}.",
        )
        answer = answer.replace("<key>", missing_key)
    else:
        formatted_identifiers = ", ".join(indentifiers)
        answer = answer.replace(
            "<initial_error>",
            f"One of dictionaries {formatted_identifiers} does not have a key with value {missing_key}.",
        )
        answer = answer.replace("<key>", missing_key)

    return answer


def handle_attr_error(error_message):
    """ docstring later on """

    quoted_words = convert(get_quoted_words(error_message))
    error = " ".join(quoted_words)
    error = slugify(error, separator="+")
    return url_for_error(error)


def handle_indentation_error(error_message):
    """ Process an IndentationError """
    message = remove_exception_from_error_message(error_message)
    return url_for_error(message)


def handle_index_error(message):
    """ Process an IndexError """

    to_remove = " cannot be "
    if to_remove in message:
        message = message.replace(to_remove, EMPTY_STRING)

    message = message.replace("IndexError:", "index error")
    message = slugify(message, separator="+")

    return url_for_error(message)


def handle_name_error(error_message: str):
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
    message = ""
    if hint1 in error_message:
        message = "must have first callable argument"
    elif hint2 in message:
        message = remove_exception_from_error_message(error_message)

    return url_for_error(error_message)


def handle_module_not_found_error(error_message):
    """Handling ModuleNoutFoundError is quite simple as most of well known packages
    already have questions on ModuleNotFoundError solved at stackoverflow"""

    message = error_message.replace("ModuleNotFoundError", EMPTY_STRING)
    return url_for_error(message)


# Helpers


def check_tokens_for_query(tokens: List) -> str:
    """  Check SyntaxError tokens to determine an apropriate query """

    query = ""

    if "for" in tokens:
        query =  "for loop"
    elif "while" in tokens:
        query = "while loop"
    elif "if" in tokens or "else" in tokens:
        query =  "if else syntax"
    elif "def" in tokens:
        query = "function definition"
    else:
        query = "SyntaxError: invalid syntax"

    return query


def convert(quoted_words: List[str]) -> List[str]:
    """Take some quoted words on the error message
    and try to translate then.
    """
    translated_words = [search_translate(w) for w in quoted_words]
    return translated_words


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

    for line in content[1:len(content)-1]:
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
    readable_data_types = [
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
        return readable_data_types[DATA_TYPES.index(word)]

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


def get_help(search, packages: defaultdict, datatypes):
    """ gets help from the Python help() """

    # TODO: Too many branches, please refactor this method

    changed = False
    path = "output.txt"
    lines = help_to_list(path, search)

    if "No Python documentation found for" in lines[0]:
        lines = []
    else:
        lines = help_to_code(search, lines)

    if not lines:
        for pckg_name in packages["import_name"]:
            try:
                pckg = import_module(pckg_name)
                search_query = pckg.__name__ + "." + search
                lines = help_to_list(path, search_query)
                if not lines:
                    break
            except:
                # TODO: what exception should pass?
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


def remove_quoted_words(error_message: str):
    """Removes quoted words from an error messsage.
    Example:
    input: "NameError: name 'a' is not defined"
    output: "NameError: name is not defined"
    """
    return re.sub(r"'.*?'\s", EMPTY_STRING, error_message)


def remove_outter_quotes(string: str) -> str:
    """This will remove both single and double quote chars
    from a string at the beggining and the end.
    Example:
    input: ('foo',) 'bar'"
    """
    return string.strip('"').strip("'")


def remove_text_between_tags(text: str, tag_name: str) -> str:
    """This will remove all text between the given tag
    Example:
    input: "foo <code>a=2;<code> bar"
    output: "foo  bar"
    """
    tag_regex = rf"<{tag_name}>(.+?)<{tag_name}>"
    return re.sub(tag_regex, EMPTY_STRING, text)
