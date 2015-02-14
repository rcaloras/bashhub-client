import os
from bashhub_globals import *
from model import UserContext
import dateutil.parser
from time import *

def build_user_context():
    ppid = os.getppid()

    # Non standard across systems GNU Date and BSD Date
    # both convert to epoch differently. Need to use
    # python date util to make standard.
    start_time_command = "ps -p {} -o lstart | sed -n 2p".format(ppid)
    date_string = os.popen(start_time_command).read().strip()
    date = dateutil.parser.parse(date_string)
    start_time = int(mktime(date.timetuple()))*1000
    return UserContext(ppid, start_time, BH_USER_ID, BH_SYSTEM_ID)
