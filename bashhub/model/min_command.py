from __future__ import annotations

from .serializable import Serializable


class MinCommand(Serializable):
    def __init__(self, command: str, created: int, uuid: str) -> None:
        self.command = command
        self.created = created
        self.uuid = uuid

    def __str__(self) -> str:
        return self.command
