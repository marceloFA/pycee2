import requests
from pydoc import help

from error_info import get_error_info, get_packages
from handle_code_errors import determine_query

# TODO: encapsulate the logic inside __main__ to 
# a new method inside query_stack_api so we can 
# dry out these coupling imports
from query_stack_api import (
    get_questions, get_links, get_post_ids,
    identify_code, replace_code, remove_tags, get_summary
)
from sym_table import get_offending_line

from utils import QUESTION_URL, ANSWER_URL
from utils import EMPTY_STRING

if __name__ == '__main__':

    error_info = get_error_info()
    offending_line = get_offending_line(error_info)
    packages = get_packages(error_info['code'])
    query, pydoc_info = determine_query(error_info, offending_line, packages)
    question = get_questions(query)   
    links = get_links(question)

    # TODO: turn this into a separate method inside query_stack_api module
    # get question ids
    question_id = get_post_ids(links)
    questions_ids = filter(lambda id: id > 0, question_id)
    questions_ids = [str(a) for a in questions_ids]
    possible_answers_ids = []
    possible_answers_bodies = []


    # getting votes to check answers have no negative votes
    for question_id in questions_ids:
        question_response = requests.get(
            QUESTION_URL.replace('id', question_id))
        question_summary=question_response.json()['items'][0]
        if 'accepted_answer_id' in question_summary:
            possible_answers_ids.append(
                str(question_summary['accepted_answer_id']))
        else:
            # TODO: if question has no accepted answer, get most voted answer then
            pass

    for answer_id in possible_answers_ids:
            answer_response=requests.get(ANSWER_URL.replace('id', answer_id))
            answer_body=answer_response.json()['items'][0]['body']
            possible_answers_bodies.append(answer_body)


    pos = identify_code(possible_answers_bodies[0])
    tester = replace_code(possible_answers_bodies[0], pos, error_info['traceback'], offending_line)
    tester = remove_tags(tester)
    
    # summarise here
    # TODO: turn this into another separate method query_stack_api
    summary = None
    if (len(tester.split('\n')) <= 4):
        summary=tester
    else:
        tmpSummary=get_summary(tester)
        summary=[]
        tmpTest=tester.replace(". ", '\n')
        for line in tmpSummary:
            for sec in tmpTest.split('\n'):
                if ((sec.lstrip() != '') and (sec.lstrip() in str(line))):
                    if ("*pre*" in str(line)):
                        sec=sec.replace("*pre*", EMPTY_STRING)
                        exists=False
                        for i in summary:
                            if (sec == i):
                                exists=True
                        if (exists == False):
                            sec=sec.replace("&gt;",">")
                            sec=sec.replace("&lt;COMMA_CHAR<")
                            summary.append(sec)
                    else:
                        exists=False

                        for i in summary:
                            if str(line) == i:
                                exists=True

                        if not exists:
                            new_line=str(line)
                            new_line=new_line.replace("&gt;",">")
                            new_line=new_line.replace("&lt;","<")
                            summary.append(new_line)
        summary='\n'.join(summary)+'\n'
    
    print('summary: \n', summary)
    
    # TODO: fix pydocs information, currently not working.
    if pydoc_info:
        print("From PyDocs")
        if (pydoc_info != []):
            print('\n'.join(pydoc_info))
