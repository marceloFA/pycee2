from httmock import urlmatch, all_requests, HTTMock
from pycee.answers import get_questions, get_answers_bodies
from pycee.utils import ANSWER_URL


# data resources
fake_answer_id = 999999
questions = {'items': [
    {'is_answered': True, 'view_count': 65, 'accepted_answer_id': 64332917, 'answer_count': 1, 'score': 2, 'question_id': 64293904,
        'link': 'https://stackoverflow.com/questions/64293904/toolchain-pythonwith-kivy-code-xcode-ios-simulator-modulenotfounderror'},
    {'is_answered': False, 'view_count': 58, 'answer_count': 0, 'score': 0, 'question_id': 61509047,
        'link': 'https://stackoverflow.com/questions/61509047/cant-import-kivy-in-pycharm-due-to-this-error-modulenotfounderror-no-module-n', },
    {'is_answered': False, 'view_count': 65, 'answer_count': 0, 'score': 0, 'question_id': 64164644,
        'link': 'https://stackoverflow.com/questions/64164644/modulenotfounderror-no-module-named-kivy-but-kivy-is-installed-in-vscode'}
]}
answers = {'items': [
    {'is_accepted': True, 'score': 0, 'answer_id': fake_answer_id, 'question_id': 64293904,
        'body': '<p>Installing....</p>\n<pre><code>pip3 install package\n</code></pre>\n'}
]}


#@urlmatch(netloc='https://fakeurl.com')
@all_requests
def fake_question_request(url, request):
    return {'status_code': 200,
            'content': questions}


#@urlmatch(netloc=ANSWER_URL.replace('<id>', str(fake_answer_id)))
@all_requests
def fake_answer_request(url, request):
    return {'status_code': 200,
            'content': answers}


def test_get_questions():

    # in the real application this is a real query to the stackexchange api
    query = 'http://fakeurl.com'
    with HTTMock(fake_question_request):
        question_ids, accepted_answer_ids = get_questions(query)

    assert question_ids == ['64293904', '61509047', '64164644']
    assert accepted_answer_ids == ['64332917']


def test_get_answers_bodies():

    answer_id = [fake_answer_id]
    with HTTMock(fake_answer_request):
        answer_bodies = get_answers_bodies(answer_id)

    assert answer_bodies == [
        '<p>Installing....</p>\n<pre><code>pip3 install package\n</code></pre>\n']
