from __future__ import annotations

from dataclasses import dataclass

from .serializable import Serializable


@dataclass
class StatusView(Serializable):
    username: str
    total_commands: int
    total_sessions: int
    total_systems: int
    total_commands_today: int
    session_name: str | None
    session_start_time: int
    session_total_commands: int
