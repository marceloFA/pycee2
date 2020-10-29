from httmock import urlmatch, all_requests, HTTMock
from pycee.answers import get_questions, get_accepted_answers
from pycee.utils import ANSWER_URL


# data resources
questions = {'items': [
    {'is_answered': True, 'view_count': 65, 'accepted_answer_id': 64332917, 'answer_count': 1, 'score': 2, 'question_id': 64293904},
    {'is_answered': False, 'view_count': 58, 'answer_count': 0, 'score': 0, 'question_id': 61509047},
    {'is_answered': False, 'view_count': 65, 'answer_count': 0, 'score': 0, 'question_id': 64164644}
]}

fake_answer_id = 999999
answers = {'items': [
    {'is_accepted': True, 'score': 0, 'answer_id': fake_answer_id, 'question_id': 64293904,
        'body': '<p>Installing....</p>\n<pre><code>pip3 install package\n</code></pre>\n'}
]}


@all_requests
def fake_question_request(url, request):
    return {'status_code': 200,
            'content': questions}


@all_requests
def fake_answer_request(url, request):
    return {'status_code': 200,
            'content': answers}


def test_get_questions_skip_unanswered_questions():

    # in the real application this is a real query to the stackexchange api
    query = 'http://fakeurl.com'
    with HTTMock(fake_question_request):
        question_ids, accepted_answer_ids = get_questions(query)

    assert question_ids == []
    assert accepted_answer_ids == ['64332917']


def test_get_accepted_answers_return_only_one_accepted_answer():

    answer_id = [fake_answer_id]
    with HTTMock(fake_answer_request):
        answer_bodies = get_accepted_answers(answer_id)

    assert answer_bodies == [
        '<p>Installing....</p>\n<pre><code>pip3 install package\n</code></pre>\n']

