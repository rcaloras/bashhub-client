import dateutil.parser
import datetime
import humanize
from ..bashhub_globals import BH_URL

status_view = """\
=== Bashhub Status
{0}/{1}
Total Commands: {2}
Total Sessions: {3}
Total Systems:  {4}
===
Session PID {5} Started {6}
Commands In Session: {7}
Commands Today: {8}
"""

def build_status_view(model):
    date = datetime.datetime.fromtimestamp(model.session_start_time / 1000.0)
    date_str = humanize.naturaltime(date)
    return status_view.format(
        BH_URL, model.username, model.total_commands, model.total_sessions,
        model.total_systems, model.session_name, date_str,
        model.session_total_commands, model.total_commands_today)
