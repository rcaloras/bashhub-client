import os
import dateutil.parser
from time import *
from .bashhub_globals import *


def get_session_information():
    ppid = os.getppid()

    # Non standard across systems GNU Date and BSD Date
    # both convert to epoch differently. Need to use
    # python date util to make standard.
    start_time_command = "ps -p {0} -o lstart | sed -n 2p".format(ppid)
    date_string = os.popen(start_time_command).read().strip()
    date = dateutil.parser.parse(date_string)
    start_time = int(mktime(date.timetuple())) * 1000
    return (ppid, start_time)
