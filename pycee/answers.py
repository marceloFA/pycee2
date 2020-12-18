"""This module contains the logic of accessing stackoverflow,
 retrieving the adequate questions for the compiler error
 and then choosing the best answer for the error"""

import re
from keyword import kwlist
from typing import List, Tuple
from operator import attrgetter
from difflib import get_close_matches

import requests
from html2text import html2text
from filecache import filecache, WEEK
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.luhn import LuhnSummarizer
from sumy.parsers.plaintext import PlaintextParser

from .utils import SINGLE_SPACE_CHAR, COMMA_CHAR, EMPTY_STRING
from .utils import BUILTINS, ANSWER_URL, QUESTION_ANSWERS_URL
from .utils import Question, Answer


def get_so_answers(query, error_info, cache=True, n_answers=3):
    """This coordinate the answer aquisition process. It goes like this:
    1- Use the query to check stackexchange API for related questions
    2- TODO: If stackoverflow API search engine couldn't find questions, ask Google instead
    3- For each question, get the most voted and accepted answers
    4- Sort answers by vote count and limit them
    3- TODO: Summarize long answers and make it ready to output to the user;
    """

    questions = None
    answers = None

    if cache:
        questions = cached_ask_stackoverflow(query)
        answers = cached_answer_content(questions)
    else:
        questions = ask_stackoverflow(query)
        answers = get_answer_content(questions)

    sorted_answers = sorted(answers, key=attrgetter("score"), reverse=True)[:n_answers]
    summarized_answers = []

    for ans in sorted_answers:
        markdown_body = html2text(ans.body)
        # TODO: summarize long answers
        summarized_answers.append(markdown_body)

    return summarized_answers, sorted_answers


def ask_stackoverflow(query: str) -> Tuple[Question, None]:
    """This method ask StackOverflow (so) API for questions."""

    if query is None:
        return tuple()

    response_json = requests.get(query).json()
    questions = []

    for question in response_json["items"]:

        if question["is_answered"]:
            questions.append(Question(id=str(question["question_id"]), has_accepted="accepted_answer_id" in question))

    return tuple(questions)


def get_answer_content(questions: Tuple[Question]) -> Tuple[Answer, None]:
    """Retrieve the most voted and the accepted answers for each question"""

    url = QUESTION_ANSWERS_URL + "&order=desc" + "&sort=votes"
    answers = []

    for question in questions:

        response = requests.get(url.replace("<id>", str(question.id)))
        items = response.json()["items"]

        if not items:
            continue

        # get most voted answer
        # first item because results are sorted by score
        answers.append(
            Answer(
                id=str(items[0]["answer_id"]),
                accepted=items[0]["is_accepted"],
                score=items[0]["score"],
                body=items[0]["body"],
                author=items[0]["owner"]["display_name"],
                profile_image=items[0]["owner"].get("profile_image", None),
            )
        )

        # oftentimes the most voted answer
        # is also the accepted asnwer
        if items[0]["is_accepted"]:
            continue

        # get accepted answer
        if question.has_accepted:
            # accepted is a filtered list of which the only and first elment is the accepted answer
            accepted = list(filter(lambda a: a["is_accepted"], items))[0]
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


@filecache(WEEK)
def cached_answer_content(*args, **kwargs):
    """ get_answer_content decorated with a cache """
    return get_answer_content(*args, **kwargs)


@filecache(WEEK)
def cached_ask_stackoverflow(*args, **kwargs):
    """ ask_stackoverflow decorated with a cache """
    return ask_stackoverflow(*args, **kwargs)
