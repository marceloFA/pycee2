"""This module contains the logic of accessing stackoverflow,
 retrieving the adequate questions for the compiler error
 and then choosing the best answer for the error"""

import re
from typing import Tuple
from operator import attrgetter

from argparse import Namespace
from filecache import filecache, MONTH
import googlesearch
from html2text import html2text
import requests

from .utils import ANSWERS_URL
from .utils import Question, Answer


def get_answers(query, error_info: dict, cmd_args: Namespace):
    """This coordinate the answer aquisition process. It goes like this:
    1- Use the query to check stackexchange API for related questions
    2- If stackoverflow API search engine couldn't find questions, ask Google instead
    3- For each question, get the most voted and accepted answers
    4- Sort answers by vote count and limit them
    3- TODO: Summarize long answers and make it ready to output to the user;
    """

    questions = answers = None

    # TODO: @marcelofa, implement a decent optional cache feature
    if cmd_args.cache:
        questions, answers = ask_cache(query, error_info, cmd_args)
    else:
        questions, answers = ask_live(query, error_info, cmd_args)

    sorted_answers = sorted(answers, key=attrgetter("score"), reverse=True)[: cmd_args.n_answers]
    summarized_answers = []

    for ans in sorted_answers:
        markdown_body = html2text(ans.body)
        # TODO: summarize long answers
        summarized_answers.append(markdown_body)

    return summarized_answers, sorted_answers


def _ask_stackoverflow(query: str) -> Tuple[Question, None]:
    """Ask StackOverflow (so) API for questions."""

    if query is None:
        return tuple()

    response_json = requests.get(query).json()
    questions = []

    for question in response_json["items"]:

        if question["is_answered"]:
            questions.append(Question(id=str(question["question_id"]), has_accepted="accepted_answer_id" in question))

    return tuple(questions)


def _ask_google(error_message: str, n_questions: int) -> Tuple[Question, None]:
    """Google errors that could not be found
    using StackOverflow API"""

    # restrict to get only results form StackOverflow
    query = error_message + " site:stackoverflow.com"
    questions_url = googlesearch.search(
        query,
    )[:n_questions]

    # parse questions id from each url path
    # re.findall will return something like '/666/' so the
    # [1:-1] slicing can remove these slashes
    questions_id = [re.findall(r"/\d+/", q)[0][1:-1] for q in questions_url]

    return tuple(Question(id=qid, has_accepted=None) for qid in questions_id)


def _get_answer_content(questions: Tuple[Question]) -> Tuple[Answer, None]:
    """Retrieve the most voted and the accepted answers for each question"""

    answers = []

    for question in questions:

        response = requests.get(ANSWERS_URL.replace("<id>", question.id))
        items = response.json()["items"]

        if items == []:
            continue
        
        # get most voted answer
        # first item because results are retrieved sorted by score
        most_voted = items[0]
        
        answers.append(
            Answer(
                id=str(most_voted["answer_id"]),
                accepted=most_voted["is_accepted"],
                score=most_voted["score"],
                body=most_voted["body"],
                author=most_voted["owner"]["display_name"],
                profile_image=most_voted["owner"].get("profile_image", None),
            )
        )

        # oftentimes the most voted answer
        # is also the accepted asnwer
        if most_voted["is_accepted"]:
            continue

        # get accepted answer, if any

        # a filtered list which the first and only element is the accepted answer
        filtered = list(filter(lambda a: a["is_accepted"], items))
        if filtered == []:
            continue

        accepted = filtered[0]
        answers.append(
            Answer(
                id=str(accepted["answer_id"]),
                accepted=True,
                score=accepted["score"],
                body=accepted["body"],
                author=accepted["owner"]["display_name"],
                profile_image=accepted["owner"].get("profile_image", None),
            )
        )

    return tuple(answers)


# Cache related code below


def ask_cache(query, error_info, cmd_args):
    """ Retrieve questions and answers from cached local files """

    questions = None
    if cmd_args.google_search_only:
        questions = _cached_ask_google(error_info["message"], cmd_args.n_questions)
    else:
        # force a google search if stackoverflow didn't provide any answer
        questions = _cached_ask_stackoverflow(query) or _cached_ask_google(error_info["message"], cmd_args.n_questions)

    answers = _cached_answer_content(questions)
    return questions, answers


def ask_live(query, error_info, cmd_args):
    """ Retrieve questions and answers by doing actual http requests """

    questions = None
    if cmd_args.google_search_only:
        questions = _ask_google(error_info["message"], cmd_args.n_questions)
    else:
        # force a google search if stackoverflow didn't provide any answer
        questions = _ask_stackoverflow(query) or _ask_google(error_info["message"], cmd_args.n_questions)

    answers = _get_answer_content(questions)
    return questions, answers


@filecache(MONTH)
def _cached_answer_content(*args, **kwargs):
    """ get_answer_content decorated with a cache """
    return _get_answer_content(*args, **kwargs)


@filecache(MONTH)
def _cached_ask_stackoverflow(*args, **kwargs):
    """ ask_stackoverflow decorated with a cache """
    return _ask_stackoverflow(*args, **kwargs)


@filecache(MONTH)
def _cached_ask_google(*args, **kwargs):
    """ ask_google decorated with a cache """
    return _ask_google(*args, **kwargs)
