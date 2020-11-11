"""This module contains the logic of accessing stackoverflow,
 retrieving the adequate questions for the compiler error
 and then choosing the best answer for the error"""

import re
from keyword import kwlist
from typing import List
from difflib import get_close_matches

import requests
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.luhn import LuhnSummarizer
from sumy.parsers.plaintext import PlaintextParser

from .utils import SINGLE_SPACE_CHAR, COMMA_CHAR, EMPTY_STRING
from .utils import BUILTINS, ANSWER_URL, QUESTION_ANSWERS_URL


def get_answers(query, traceback, offending_line):
    """This coordinate the answer aquisition process. It goes like this:
    1- Use the query to check stackexchange API for related questions;
    2.1- Get answers from questions with accepted answers;
    2.1- Get most voted answers from questions without accepted answers;
    3- Summarize the answers and make it ready to output to the user;
    """
    questions_ids, accepted_answer_ids = get_questions(query)
    accepted_answers_bodies = get_accepted_answers(accepted_answer_ids)
    other_answers_bodies = get_most_voted_answers(questions_ids)

    answers = []
    for body in accepted_answers_bodies + other_answers_bodies:
        code_position = identify_code(body)
        tester = replace_code(body, code_position, traceback, offending_line)
        answer_body = remove_tags(tester)
        answers.append(answer_body)

    return answers


def get_questions(query):
    """This method ask stackexchange API for questions.
    It then return the answers ids for questions with an accepted answer
    and questions ids for questions with no accepted answer.
    Sorted by vote count."""

    response = requests.get(query)
    response_json = response.json()

    accepted_answer_ids = []
    question_ids = []
    for question in response_json["items"]:

        if not question["is_answered"]:
            pass
        elif "accepted_answer_id" in question:
            field = str(question["accepted_answer_id"])
            accepted_answer_ids.append(field)
        else:
            # if question has no accepted answer, get most voted answer later
            field = str(question["question_id"])
            question_ids.append(field)

    return question_ids, accepted_answer_ids


def get_accepted_answers(accepted_answer_ids: List[str]) -> List[str]:
    """Take an accepted answer id and return the body of it."""

    answers_bodies = []
    for id_ in accepted_answer_ids:
        response = requests.get(ANSWER_URL.replace("<id>", str(id_)))
        answer_body = response.json()["items"][0]["body"]
        answers_bodies.append(answer_body)

    return answers_bodies


def get_most_voted_answers(questions_ids: List[str]) -> List[str]:
    """Take an accepted answer id and return the body of it.
    As we want only the most voted answer, we can order by vote count
    and limit ansers by one.
    """
    page_size = "&pagesize=1"
    order = "&order=desc"
    url = QUESTION_ANSWERS_URL + page_size + order

    answers_bodies = []
    for id_ in questions_ids:
        response = requests.get(url.replace("<id>", str(id_)))
        answer_body = response.json()["items"][0]["body"]
        answers_bodies.append(answer_body)
    return answers_bodies


def parse_summarizer(answer_body):
    """Method to summary an answer body
    and remove html tags and formating.
    TODO: has not been refactored yet
    """
    summary = None
    if len(answer_body.split("\n")) <= 4:
        summary = answer_body
    else:
        tmp_summary = get_summary(answer_body)
        summary = []
        temp_test = answer_body.replace(". ", "\n")
        for line in tmp_summary:
            for sec in temp_test.split("\n"):
                if (sec.lstrip() != "") and (sec.lstrip() in str(line)):
                    if "*pre*" in str(line):
                        sec = sec.replace("*pre*", EMPTY_STRING)
                        exists = False
                        for i in summary:
                            if sec == i:
                                exists = True
                        if not exists:
                            sec = sec.replace("&gt;", ">")
                            sec = sec.replace("&lt;COMMA_CHAR<")
                            summary.append(sec)
                    else:
                        exists = False

                        for i in summary:
                            if str(line) == i:
                                exists = True

                        if not exists:
                            new_line = str(line)
                            new_line = new_line.replace("&gt;", ">")
                            new_line = new_line.replace("&lt;", "<")
                            summary.append(new_line)
        summary = "\n".join(summary) + "\n"

    return summary


def get_summary(sentences):
    """Convert sentences to single string -> not good for code."""

    parser = PlaintextParser.from_string(sentences, Tokenizer("english"))
    length = 4  # halve length and round up
    # summarise text
    summariser = LuhnSummarizer()

    return summariser(parser.document, length)


# Answer parsing


def identify_code(text):
    """Retrieve code from the answer body."""

    start_tag = "<code>"
    end_tag = "</code>"
    pos = []  # list to hold code positions

    if start_tag in text:
        for i, char in enumerate(text):
            if char == "<":
                if start_tag == text[i : i + len(start_tag)]:
                    pos.append([])
                    pos[len(pos) - 1].append(i + len(start_tag))
                    if text[i - 5 : i] == "<pre>":
                        pos[len(pos) - 1].append(1)
                    else:
                        pos[len(pos) - 1].append(0)
                if end_tag == text[i : i + len(end_tag)]:
                    pos[len(pos) - 1].append(i)

        for i in range(0, len(pos)):
            tmp = pos[i][2]
            pos[i][2] = pos[i][1]
            pos[i][1] = tmp
    return pos


def remove_tags(text):
    """ docstring later on """

    text = text.replace("<pre>", "*pre*")
    text = text.replace("</pre>", "*pre*")
    cleaner = re.compile("<.*?>")
    clean_text = re.sub(cleaner, "", text)
    return clean_text


def replace_code(text, pos, message, offending_line):
    """ docstring and refactor work later on """

    new_text = text
    no_tags = remove_tags(text)
    no_tags_lines = no_tags.split("\n")
    error_lines = message.split("\n")
    error_type = None
    for line in error_lines:
        if "Error: " in line:
            error_type = line.split(SINGLE_SPACE_CHAR, 1)[0]

    error_header = error_lines[1]
    qa_offending_line = None  # Syntax Error only
    qa_error_line = None

    # check for compiler text in question/answer
    regex = r"(File|Traceback)(.+)\n(.+)((\n)|(\n( |\t)+\^))\n(Arithmetic|FloatingPoint|Overflow|ZeroDivision|Assertion|Attribute|Buffer|EOF|Import|ModuleNotFound|Lookup|Index|Key|Memory|Name|UnboundLocal|OS|BlockingIO|ChildProcess|Connection|BrokenPipe|ConnectionAborted|ConnectionRefused|ConnectionReset|FileExists|FileNotFound|Interrupted|IsADirectory|NotADirectory|Permission|ProcessLookup|Timeout|Reference|Runtime|NotImplemented|Recursion|Syntax|Indentation|Tab|System|Type|Value|Unicode|UnicodeDecode|UnicodeEncode|UnicodeTranslate)(Error:)(.+)"
    match = re.search(regex, no_tags)
    if match:
        qa_error_line = match.group(0).split("\n")[1]
        # ALSO CHECK QUESTION?

    # if SyntaxError we may need to handle differently
    if error_type == "SyntaxError:" and qa_error_line:
        if error_header != offending_line:
            for i in range(len(pos)):
                previous = None
                if bool(pos[i][2]) and (match.group(0) not in text[pos[i][0] : pos[i][1]]):
                    for line in text[pos[i][0] : pos[i][1]].split("\n"):
                        if line == qa_error_line:
                            qa_offending_line = previous
                        previous = line

            # check previous line
            # if previous line of code, swap and exit
            if qa_offending_line:
                qa_offending_line = qa_offending_line.strip()
            if error_header:
                error_header = error_header.strip()
            if qa_error_line:
                qa_error_line = qa_error_line.strip()

            for i in reversed(pos):
                j = pos.index(i)
                if qa_offending_line in text[pos[j][0] : pos[j][1]]:
                    new_text = new_text[: pos[j][0]] + error_header + new_text[pos[j][1] :]
                elif qa_error_line in text[pos[j][0] : pos[j][1]]:
                    new_text = new_text[: pos[j][0]] + offending_line + new_text[pos[j][1] :]
            return new_text

    if qa_error_line is None:
        tmpqa_error_line = get_close_matches(offending_line, no_tags_lines, 1, 0.4)
        if tmpqa_error_line:
            qa_error_line = tmpqa_error_line[0]

    if (qa_error_line is None) or (qa_error_line == ""):
        return text
    # if exists, check for similar lines
    possible_lines = []
    if qa_error_line is None:
        possible_lines = get_close_matches(qa_error_line, no_tags_lines, 3, 0.4)
    # if exists, substitute variables
    if len(possible_lines) > 0 or qa_error_line:
        # tokenise similar to before, may have to group
        user_variables = []
        usr_builtins = []
        tokens = re.split(r"[!@#$%^&*_\-+=\(\)\[\]\{\}\\|~`/?.<>:; ]", error_header)
        for token in reversed(tokens):
            if (token not in kwlist) and (token not in BUILTINS):
                user_variables.append(token)
            else:
                usr_builtins.append(token)
        user_variables = list(reversed(user_variables))
        usr_builtins = list(reversed(usr_builtins))
        # split
        qa_line = None
        if qa_error_line:
            qa_line = qa_error_line
        else:
            qa_line = possible_lines[0]
        if "," in qa_line:
            while (", " in qa_line) or (" ," in qa_line):
                qa_line = qa_line.replace(", ", COMMA_CHAR)
                qa_line = qa_line.replace(" ,", COMMA_CHAR)
        qa_variables = []
        tokens = re.split(r"[!@#$%^&*_\-+=\(\)\[\]\{\}\\|~`/?.<>:; ]", qa_line)
        for token in reversed(tokens):
            if (token not in kwlist) and (token not in BUILTINS):
                qa_variables.append(token)
        qa_variables = list(reversed(qa_variables))

        for word in reversed(qa_variables):
            if word == "":
                qa_variables.remove(word)

        for word in reversed(user_variables):
            if not word:
                user_variables.remove(word)

        newqa_line = qa_line
        if len(user_variables) == len(qa_variables):
            for word, i in enumerate(qa_variables):
                newqa_line.replace(word, user_variables[i])

    return new_text
