from pycee.answers import get_so_answers
from pycee.errors import handle_error
from pycee.inspection import get_error_info, get_packages
from pycee.utils import parse_args, remove_cache, print_answers


def main():

    args = parse_args()

    if args.rm_cache:
        remove_cache()

    error_info = get_error_info(args.file_name)
    query, pycee_hint, pydoc_answer = handle_error(error_info, n_questions=args.n_questions, dry_run=args.dry_run)
    so_answers, _ = get_so_answers(
        query,
        error_info,
        cache=args.cache,
        n_answers=args.n_answers,
    )
    print_answers(so_answers, pycee_hint, pydoc_answer, args)


if __name__ == "__main__":
    main()
