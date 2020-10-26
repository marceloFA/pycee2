import requests
from pydoc import help

from error_info import get_error_info, get_packages
from code_errors import determine_query
# TODO: encapsulate the logic inside __main__ to 
# a new method inside query_stack_api so we can 
# dry out these coupling imports
from answers import get_answers
from sym_table import get_offending_line
from utils import QUESTION_URL, ANSWER_URL
from utils import EMPTY_STRING

if __name__ == '__main__':

    error_info = get_error_info()
    offending_line = get_offending_line(error_info)
    packages = get_packages(error_info['code'])
    query, pydoc_info = determine_query(error_info, offending_line, packages)
    answers = get_answers(query, error_info['traceback'], offending_line)
    
    for i, answer in enumerate(answers):
        print(f'\n\nSolution {i}:')
        print(answer)
    
    # TODO: fix pydocs information, currently not working.
    if pydoc_info:
        print("From PyDocs")
        if (pydoc_info != []):
            print('\n'.join(pydoc_info))
