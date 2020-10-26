''' This module contains all the logic that hadles code errors '''
import re
import sys
from json import load
from os.path import join
from typing import List, Union
from keyword import kwlist

from difflib import get_close_matches
from slugify import slugify

from utils import get_project_root, DATA_TYPES, BUILTINS
from utils import (
    SINGLE_QUOTE_CHAR, DOUBLE_QUOTE_CHAR,
    SINGLE_SPACE_CHAR, EMPTY_STRING,
    COMMA_CHAR
)

# Stack Overflow URL for scraping
api_base_url = 'https://api.stackexchange.com/2.2/search?site=stackoverflow' 
base_url = "https://stackoverflow.com"
search_url = "/search?q="


def determine_query(error_info: dict, offending_line:int, packages) -> str:
    ''' choose the correct query to run based on the error type '''
    
    pydoc_info = None
    error_type = error_info['type']
    error_message = error_info['message']
    traceback = error_info['traceback']

    if error_type == "SyntaxError:":
        query = get_syntax_error(error_message, offending_line)

    elif error_type == "TabError:":
        query = get_tab_error(error_message)

    elif error_type == "IndentationError:":
        query = get_indentation_error(error_message)

    elif error_type == "IndexError:":
        query = get_index_error(error_message)

    elif error_type == "AttributeError:":
        query = get_attr_err(error_message)
        search = convert(extract(traceback))[1]
        search = search.replace(SINGLE_QUOTE_CHAR, EMPTY_STRING)
        search = check_functions(search)  # originally words
        if search:
            pydoc_info = get_help(search, packages, DATA_TYPES)

    elif error_type == "NameError:":
        query=get_name_error(error_message)
        search=convert(extract(traceback))[0]
        search=check_functions(search)  # originally words
        if search:
            pydoc_info = get_help(search, packages, DATA_TYPES)
    else:
        # default query
        query=get_query(error_message, error_type)
    
    return query, pydoc_info


def get_query(error_message: str, error_type:str):
    ''' Generates the url for the query '''
    
    # remove quotation marks for specific errors
    if error_type == "KeyError":

        # check for quotation marks which will contain code specific data for specific error
        while SINGLE_QUOTE_CHAR in error_message:
            start = error_message.find(SINGLE_QUOTE_CHAR)
            end = error_message[start+1:].find(SINGLE_QUOTE_CHAR)+start+2
            error_message = error_message.replace(error_message[start:end], EMPTY_STRING)

        while DOUBLE_QUOTE_CHAR in error_message:
            start = error_message.find(DOUBLE_QUOTE_CHAR)
            end = error_message[start+1:].find(DOUBLE_QUOTE_CHAR)+start+2
            error_message = error_message.replace(error_message[start:end], EMPTY_STRING)

    return url_for_error(error_message)


def get_attr_err(message):
    ''' docstring later on '''

    variables=convert(extract(message))
    error=''

    for var in variables:
        error=error + SINGLE_SPACE_CHAR + var

    error=error.replace(SINGLE_SPACE_CHAR, "+")
    error=error.replace(SINGLE_QUOTE_CHAR, EMPTY_STRING)

    return url_for_error(error)

def get_indentation_error(message):
    ''' docstring later on '''

    error_type=message.split(SINGLE_SPACE_CHAR, 1)[0]
    message=message.replace(error_type, EMPTY_STRING)

    return url_for_error(message)

def get_index_error(message):
    ''' docstring later on '''

    to_remove=" cannot be "
    if to_remove in error:
        error=message.replace(to_remove, EMPTY_STRING)

    error=message.replace("IndexError: ","index error ")
    error=error.replace(SINGLE_SPACE_CHAR, "+")

    return url_for_error(error)

def get_name_error(message):
    ''' docstring later on '''

    variables=[]
    query=''

    if SINGLE_QUOTE_CHAR in message:

        variables=convert(extract(message))
        toAdd=None

        if len(variables) > 1:
            toAdd = get_action_word(variables[0], variables[1])
        else:
            toAdd = get_action_word(variables[0])

        if not toAdd:
            return url_for_error("NameError")

        query=query + toAdd + ' to ' + variables[0]
        return url_for_error(query)

    # generic name error search
    else:
        return url_for_error("NameError")


def check_tokens_for_query(possibilities: List) -> str:
    ''' This will check SyntaxError tokens
        and return the apropriate query
    '''

    for word in possibilities:
        if word == 'for':
            return "for loop"
        elif word == 'while':
            return "while loop"
        elif word == 'if' or word == 'else':
            "else if syntax"
        elif word == 'def':
            isDef=True
        elif (isDef):
            # TODO: implement this correctly
            return "SyntaxError: invalid syntax"
        else:
            # Generic syntax error
            return "SyntaxError: invalid syntax"


def get_syntax_error(message, offending_line):
    ''' docstring later on '''

    # unmathcing number of quotation marks error
    single = offending_line.count(SINGLE_QUOTE_CHAR)
    double = offending_line.count(DOUBLE_QUOTE_CHAR)
    
    odd_count_quote_count=(single + double) % 2 == 1
    if odd_count_quote_count:
        return url_for_error("quotation marks")

    # unmathcing number of parenthese, brackets or braces error
    opening_brackets = offending_line.count(
        "(") + offending_line.count("[") + offending_line.count("{")
    closing_bracket = offending_line.count(
        ")") + offending_line.count("]") + offending_line.count("}")
    
    unmatching_brackets=opening_brackets != closing_bracket
    if unmatching_brackets:
        return url_for_error("bracket meanings")

    # split offendingline and remove symbols
    # what does this matches?
    regex=r'[!@#$%^&*_\-+=\(\)\[\]\{\}\\|~`/?.,<>:; ]'
    tokens=re.split(regex, offending_line)
    # remove strings/quotes
    for token in tokens:
        if (SINGLE_QUOTE_CHAR in token) or (DOUBLE_QUOTE_CHAR in token):
            tokens.remove(token)
    # then find possibilites for each word
    possibilites=[]
    for token in tokens:
        possible=[]
        possible.extend(get_close_matches(
            token.lower(), kwlist, 3, 0.6))
        possible.extend(get_close_matches(
            token.lower(), BUILTINS, 3, 0.6))

        # if exact match, only keep that word
        flag=False
        for word in possible:
            if word == token:
                possibilites.append(word)
                flag=True
        if not flag:
            possibilites.extend(possible)

    query=check_tokens_for_query(possibilites)
    return url_for_error(query)


def get_tab_error(message):
    ''' docstring later '''
    error_type=message.split(SINGLE_SPACE_CHAR, 1)[0]
    message=message.remove(error_type, EMPTY_STRING)
    return url_for_error(message)


def wor(message):
    ''' docstring later '''
    # lot to do here
    hint1="the first argument must be callable"
    hint2="not all arguments converted during string formatting"
    error_type=message.split(SINGLE_SPACE_CHAR, 1)[0]

    if hint1 in message:
        return url_for_error("must have first callable argument")
    elif hint2 in message:
        message=message.remove(error_type, EMPTY_STRING)
        return url_for_error(message)
    else:
        # generic search
        return url_for_error(message)


#### Helpers

def convert(temp_variables):
    ''' docstring later '''

    variables=[]

    for var in temp_variables:
        # originally functions
        new_word = check_functions(var.lower())
        if new_word:
            variables.append(new_word)
        else:
            variables.append(var)

    return variables

def extract(message):
    ''' docstring later'''
    variables=[]

    while SINGLE_QUOTE_CHAR in message:
        start=message.find(SINGLE_QUOTE_CHAR)
        end=message[start+1:].find(SINGLE_QUOTE_CHAR)+start+2
        word=message[start:end]
        variables.append(word)
        message=message.replace(message[start:end], '')
    return variables

def get_query_params(error_message:str):
    ''' preps the query to include necessary filters and meet URL format '''

    # old "https://stackoverflow.com/search?q=[python]+answers:1..+ModuleNotFoundError:+No+module+named+'kivy'"
    # new  https://api.stackexchange.com/2.2/search?site=stackoverflow&order=desc&sort=votes&tagged=python&intitle=ModuleNotFoundError:+No+module+named+%27kivy%27

    error_message_slug = slugify(error_message, separator='+')
    order = '&order=desc'
    sort = '&sort=votes'
    python_tagged = '&tagged=python'
    intitle = f'&intitle={error_message_slug}'
    
    return order + sort + python_tagged + intitle


def get_action_word(search1=None, search2=None) -> Union[None]:
    ''' Returns action word associated with input '''

    if not search1 and not search2:
        return None

    try:
        with open(os.path.join(get_project_root(), "python_tasks.txt"), 'rb') as temp_content:
            temp_content = temp_content.read().decode('utf-8', errors='ignore').split('\n')
    except:
        return None

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
        c1 = not search1 and search2 in line[2]
        c2 = not search2 and search1 in line[1]
        c4 = search1 and search2
        c5 = search1 in line[1] and search2 in line[2]
        c3 = c4 and c5

        if c1 or c2 or c3:
            if (line[0] not in actions):
                actions.append(line[0])
                counter.append(1)
            else:
                counter[actions.index(
                    line[0])] = counter[actions.index(line[0])] + 1

    if not counter:
        return None

    # return the max found amongst results
    return actions[counter.index(max(counter))]

def check_functions(word:str):

    word=word.lstrip().lower()
    word=word.replace(SINGLE_QUOTE_CHAR, EMPTY_STRING)
    return search_translate(word)


def search_translate(word: str) -> Union[str, None]:
    ''' Searches data from website or data types '''

    # syntax from http://rigaux.org/language-study/syntax-across-languages.html#StrngCSTSSASn
    # first entry is python, rest are other langauges
    with open(join(get_project_root(), 'syntax_across_languages.json'), 'r') as file:
        syntax_across_languages = load(file)

    word = word.lower()
    readable_DATA_TYPES = [
        'integer', 'float', 'complex',
        'boolean', 'string', 'bytes',
        'list', 'tuple', 'set', 'dictionary'
    ]

    if word in DATA_TYPES:
            return readable_DATA_TYPES[DATA_TYPES.index(word)]

    if syntax_across_languages:
        # search through provided list
        for lst in syntax_across_languages:
            if word in lst:
                return lst[0]

        # if no match, find containing
        for lst in syntax_across_languages:
            for l in lst:
                if word in l:
                    return lst[0]

    return None


def url_for_error(query: str) -> str:
    ''' Sets a valid search url '''
    
    return api_base_url + get_query_params(query)


def get_help(search, packages, datatypes):
    ''' gets help from the Python help() '''

    changed = False
    path = 'output.txt'
    lines = help_to_list(path, search)

    if "No Python documentation found for" in lines[0]:
        lines = []
    else:
        lines = help_to_code(search, lines)

    if not lines:
        for pckg_name in packages:
            try:
                pckg = importlib.import_module(pckg_name)
                search_query = pckg.__name__+'.' + search
                lines = help_to_list(path, search_query)
                if not lines:
                    break
            except:
                pass

        if not lines:
            for types in datatypes:
                search_query = types + '.' + search
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
    ''' Converts the help() format to an easy to use list '''

    with open(path, "w") as f:
        sys.__stdout__ = sys.stdout
        sys.stdout = f
        help(search)

    sys.stdout = sys.__stdout__

    with open(path) as f:
        lines = f.read().splitlines()

    return lines if lines else None


def help_to_code(search, lines):
    ''' Extracts the code from a list of help() data '''
    res = []

    if (len(lines) <= 2):
        return res

    if 'class ' + search in lines[2]:
        i = 3
        while lines[i].strip(" |"):
            res.append(lines[i].strip(" |"))
            i += 1

    elif search + ' = ' in lines[2]:
        res.append(lines[3].strip(" |"))

    if len(res) and not res[0]:
        del res[0]

    return res