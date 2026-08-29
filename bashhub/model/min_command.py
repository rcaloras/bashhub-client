from __future__ import annotations

from dataclasses import dataclass

from .serializable import Serializable


@dataclass
class MinCommand(Serializable):
    command: str
    created: int
    uuid: str

    def __str__(self) -> str:
        return self.command
