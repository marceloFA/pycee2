from pycee.answers import get_answers
from pycee.errors import handle_error
from pycee.inspection import get_error_info, get_packages
from pycee.sym_table import get_offending_line
from pycee.utils import parse_args, remove_cache, print_answers


def main():

    args = parse_args()
    if args.rm_cache:
        remove_cache()
    error_info = get_error_info(args.file_name)
    offending_line = get_offending_line(error_info)
    packages = get_packages(error_info["code"])
    query, pycee_answer, pydoc_answer = handle_error(
        error_info, offending_line, packages, limit=args.n_questions, dry_run=args.dry_run
    )
    so_answers = get_answers(
        query,
        error_info["traceback"],
        offending_line,
        error_info["message"],
        cache=args.cache,
        n_answers=args.n_answers,
    )
    print_answers(so_answers, pycee_answer, pydoc_answer, args)


if __name__ == "__main__":
    main()
