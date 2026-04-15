from __future__ import annotations

from .serializable import Serializable


class StatusView(Serializable):
    def __init__(self,
                 username: str,
                 total_commands: int,
                 total_sessions: int,
                 total_systems: int,
                 total_commands_today: int,
                 session_name: str | None,
                 session_start_time: int,
                 session_total_commands: int) -> None:
        self.username = username
        self.total_commands = total_commands
        self.total_sessions = total_sessions
        self.total_systems = total_systems
        self.total_commands_today = total_commands_today
        self.session_name = session_name
        self.session_start_time = session_start_time
        self.session_total_commands = session_total_commands
