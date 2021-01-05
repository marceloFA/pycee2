from pycee import errors


def test_handle_zero_division_error():
    assert (
        errors.handle_zero_division_error("ZeroDivisionError: division by zero")
        == "https://api.stackexchange.com/2.2/search?site=stackoverflow&order=desc&sort=relevance&tagged=python&intitle=division+by+zero"
    )
