from httmock import all_requests, HTTMock
from pycee.answers import ask_stackoverflow, get_answer_content
from pycee.utils import ANSWER_URL, Question, Answer


# data resources
fake_query = "http://fakeurl.com"
empty_questions = {"items": []}
empty_answers = {"items": []}

questions_data = {
    "items": [
        {
            "is_answered": True,
            "accepted_answer_id": 4,
            "answer_count": 1,
            "question_id": 1,
        },
        {
            "is_answered": False,
            "answer_count": 0,
            "score": 0,
            "question_id": 2,
        },
    ]
}
answers_data = {
    "items": [
        {
            "is_accepted": False,
            "score": 20,
            "answer_id": 4,
            "question_id": 1,
            "body": "Body 4",
            "owner": {
                "display_name": "author 4",
                "profile_image": "foo 4",
            },
        },
        {
            "is_accepted": True,
            "score": 10,
            "answer_id": 3,
            "question_id": 1,
            "body": "Body 3",
            "owner": {
                "display_name": "author 3",
            },
        },
        {
            "is_accepted": False,
            "score": 5,
            "answer_id": 5,
            "question_id": 1,
            "body": "Body 5",
            "owner": {
                "display_name": "author 5",
                "profile_image": "foo 5",
            },
        },
    ]
}

# mocks


@all_requests
def question_response(url, request):
    return {"status_code": 200, "content": questions_data}


@all_requests
def empty_question_response(url, request):
    return {"status_code": 200, "content": empty_questions}


@all_requests
def answer_response(url, request):
    return {"status_code": 200, "content": answers_data}


@all_requests
def empty_answers_response(url, request):
    return {"status_code": 200, "content": empty_answers}


# tests


def test_ask_stackoverflow_skip_unanswered_questions():

    question_obj = tuple([Question(id="1", has_accepted=True)])
    with HTTMock(question_response):
        questions = ask_stackoverflow(fake_query)
    assert questions == question_obj


def test_ask_stackoverflow_can_handle_empty_response():

    with HTTMock(empty_question_response):
        questions = ask_stackoverflow(fake_query)
    assert questions == tuple([])


def test_get_answer_content_from_one_question():

    question_obj = tuple([Question(id=1, has_accepted=True)])
    with HTTMock(answer_response):
        answers = get_answer_content(question_obj)

    expected_answers = [
        Answer(id="4", accepted=False, score=20, body="Body 4", author="author 4", profile_image="foo 4"),
        Answer(id="3", accepted=True, score=10, body="Body 3", author="author 3", profile_image=None),
    ]
    assert answers == tuple(expected_answers)


def test_get_answer_content_handle_empty_response():

    question_obj = tuple([Question(id=1, has_accepted=True)])
    with HTTMock(empty_answers_response):
        questions = get_answer_content(question_obj)
    assert questions == tuple([])
