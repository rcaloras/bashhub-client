from __future__ import annotations

from .min_command import MinCommand
from .serializable import Serializable


class Command(Serializable):
    def __init__(self,
                 command: str,
                 path: str,
                 uuid: str,
                 username: str,
                 system_name: str,
                 session_id: str,
                 created: int,
                 id: int,
                 exit_status: int | None = None) -> None:
        self.command = command
        self.path = path
        self.uuid = uuid
        self.exit_status = exit_status
        self.username = username
        self.system_name = system_name
        self.session_id = session_id
        self.created = created
        self.id = id

    # Optional fields not set by jsonpickle.
    exit_status: int | None = None

    def to_min_command(self) -> MinCommand:
        return MinCommand(self.command, self.created, self.uuid)


class RegisterUser(Serializable):
    def __init__(self, email: str, username: str, password: str,
                 registration_code: str = "") -> None:
        self.email = email
        self.username = username
        self.password = password
        self.registration_code = registration_code


class LoginForm(Serializable):
    def __init__(self, username: str, password: str,
                 mac: str | None = None) -> None:
        self.username = username
        self.password = password
        self.mac = mac


class LoginResponse(Serializable):
    def __init__(self, access_token: str) -> None:
        self.access_token = access_token
