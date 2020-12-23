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
    # tests that boolean arguements can change as expected

    expected_args = Namespace(
        file_name="foo.py",  # mandatory
        cache=False,  # default is True
        dry_run=True,  # default is False
        rm_cache=True,  # default is False
        google_search_only=True,  # default is False
        show_pycee_hint=False,  # default is True
        show_so_answer=False,  # default is True
    )
    parsed_args = parse_args(["foo.py", "-f", "--dry-run", "-rm", "-g", "-s", "-p"])

    assert parsed_args.cache == expected_args.cache
    assert parsed_args.dry_run == expected_args.dry_run
    assert parsed_args.rm_cache == expected_args.rm_cache
    assert parsed_args.google_search_only == expected_args.google_search_only
    assert parsed_args.show_pycee_hint == expected_args.show_pycee_hint
    assert parsed_args.show_so_answer == expected_args.show_so_answer


def test_default_args():
    expected_args = Namespace(
        file_name="foo.py",  # not an default arg, actually
        n_answers=3,
        n_questions=3,
        cache=True,
        dry_run=False,
        rm_cache=False,
        google_search_only=False,
        show_pycee_hint=True,
        show_so_answer=True,
    )
    parsed_args = parse_args(["foo.py"])

    assert parsed_args.file_name == expected_args.file_name
    assert parsed_args.n_answers == expected_args.n_answers
    assert parsed_args.n_questions == expected_args.n_questions
    assert parsed_args.cache == expected_args.cache
    assert parsed_args.dry_run == expected_args.dry_run
    assert parsed_args.rm_cache == expected_args.rm_cache
    assert parsed_args.google_search_only == expected_args.google_search_only
    assert parsed_args.show_pycee_hint == expected_args.show_pycee_hint
    assert parsed_args.show_so_answer == expected_args.show_so_answer
