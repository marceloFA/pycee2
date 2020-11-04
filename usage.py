from pycee.answers import get_answers
from pycee.errors import handle_error
from pycee.inspection import get_error_info, get_packages
from pycee.sym_table import get_offending_line

if __name__ == '__main__':
    error_info = get_error_info()
    offending_line = get_offending_line(error_info)
    packages = get_packages(error_info['code'])
    query, pycee_answer, pydoc_answer = handle_error(error_info, offending_line, packages, limit=3)
    
    if query:
        answers = get_answers(query, error_info['traceback'], offending_line)
        
        for i, answer in enumerate(answers):
            print(f'Solution {i}:')
            print(answer)
    
    if pycee_answer:
        print(pycee_answer)

    # TODO: fix pydocs information, currently not working.
    if pydoc_answer:
        print("From PyDocs")
        print('\n'.join(pydoc_answer))
