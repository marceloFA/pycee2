from pycee import errors


def test_handle_type_error():
    assert (
        errors.handle_type_error("TypeError: unsupported operand type(s) for +: 'int' and 'str'")
        == "https://api.stackexchange.com/2.2/search?site=stackoverflow&order=desc&sort=relevance&tagged=python"
        "&intitle=typeerror+unsupported+operand+type+s+for+int+and+str"
    )
