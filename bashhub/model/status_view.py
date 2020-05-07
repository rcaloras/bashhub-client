from .serializable import Serializable


class StatusView(Serializable):
    def __init__(self, username, total_commands, total_sessions, total_systems,
                 total_commands_today, session_name, session_start_time,
                 session_total_commands):
        self.username = username
        self.total_commands = total_commands
        self.total_sessions = total_sessions
        self.total_systems = total_systems
        self.total_commands_today = total_commands_today
        self.session_name = session_name
        self.session_start_time = session_start_time
        self.session_total_commands = session_total_commands
