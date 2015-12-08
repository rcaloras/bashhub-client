
from bashhub.bashhub import bashhub_globals

def test_is_valid_regex():
    invalid_regex = '[a-2]'
    valid_regex = '(filter_me|ssh)'
    assert False == bashhub_globals.is_valid_regex(invalid_regex)
    assert True == bashhub_globals.is_valid_regex(valid_regex)


