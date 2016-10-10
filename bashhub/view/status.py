import dateutil.parser
import datetime
import humanize

status_view = """\
=== Bashhub Status
https://bashhub.com/{0}
Total Commands: {1}
Total Sessions: {2}
Total Systems:  {3}
===
Session PID {4} Started {5}
Commands In Session: {6}
Commands Today: {7}
"""

def build_status_view(model):
    date = datetime.datetime.fromtimestamp(model.session_start_time / 1000.0)
    date_str = humanize.naturaltime(date)
    return status_view.format(
        model.username, model.total_commands, model.total_sessions,
        model.total_systems, model.session_name, date_str,
        model.session_total_commands, model.total_commands_today)
