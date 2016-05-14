from bashhub.shell_utils import get_session_information
from bashhub.bashhub_globals import current_milli_time


def test_get_session_information():
    session_info = get_session_information()
    process_id = session_info[0]
    process_start_time = session_info[1]
    # The session's process Id should be fairly high
    assert process_id > 0
    # The session's start time should be less than this
    assert process_start_time < current_milli_time()
