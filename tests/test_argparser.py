from argparse import Namespace
import pytest
from pycee.utils import parse_args


def test_missing_filename_raises_sys_exit():
    with pytest.raises(SystemExit):
        parse_args([])


def test_negative_number_of_answers_raises_sys_exit(capsys):
    with pytest.raises(SystemExit):
        parse_args(["foo.py", "-n", "-1"])
        out, err = capsys.readouterr()
        assert "invalid choice" in err


def test_negative_number_of_questions_raises_sys_exit(capsys):
    with pytest.raises(SystemExit):
        parse_args(["foo.py", "-q", "-1"])
        out, err = capsys.readouterr()
        assert "invalid choice" in err


def test_store_boolean_args():
    # tests that boolean arguemets are changes as needed
    default_args = Namespace(
        cache=False,  # default is True
        dry_run=True,  # default is False
        file_name="foo.py",  # not an default arg, actually
        n_answers=3,
        n_questions=3,
        rm_cache=True,  # default is False
        show_pycee_answer=False,  # default is True
        show_so_answer=False,  # default is True
    )
    assert parse_args(["foo.py", "--no-cache", "--dry-run", "-rm", "-s", "-p"]) == default_args


def test_default_args():
    default_args = Namespace(
        cache=True,
        dry_run=False,
        file_name="foo.py",  # not an default arg, actually
        n_answers=3,
        n_questions=3,
        rm_cache=False,
        show_pycee_answer=True,
        show_so_answer=True,
    )
    assert parse_args(["foo.py"]) == default_args
