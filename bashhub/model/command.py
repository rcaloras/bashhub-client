from __future__ import annotations

from dataclasses import dataclass

from .min_command import MinCommand
from .serializable import Serializable


@dataclass
class Command(Serializable):
    """A saved command, as returned by GET /api/v1/command/<uuid>.

    Fields mirror that response exactly. systemName/sessionId come back null
    when the command has no system or session attached, and exitStatus is
    null for commands recorded without one."""

    command: str
    path: str
    uuid: str
    username: str
    created: int
    system_name: str | None = None
    session_id: str | None = None
    exit_status: int | None = None

    def to_min_command(self) -> MinCommand:
        return MinCommand(self.command, self.created, self.uuid)


@dataclass
class RegisterUser(Serializable):
    email: str
    username: str
    password: str
    registration_code: str = ""


@dataclass
class LoginForm(Serializable):
    username: str
    password: str
    mac: str | None = None


@dataclass
class LoginResponse(Serializable):
    access_token: str
