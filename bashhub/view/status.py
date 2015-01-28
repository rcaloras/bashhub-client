import dateutil.parser
import datetime
import humanize

status_view ="""\
=== Bashhub Status
Logged in as {}
Total Commands: {}
Total Sessions: {}
Total Systems:  {}
===
Session PID {} Started {}
Commands In Session: {}
Commands Today: {}
"""

def build_status_view(model):
    date = datetime.datetime.fromtimestamp(model.session_start_time/1000.0)
    date_str = humanize.naturaltime(date)
    return status_view.format(model.username,  model.total_commands,
            model.total_sessions, model.total_systems,  model.session_name,
            date_str, model.session_total_commands, model.total_commands_today)

