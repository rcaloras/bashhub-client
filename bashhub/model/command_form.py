from __future__ import annotations

import uuid as uuid_module
from dataclasses import dataclass, field
from time import time

from .serializable import Serializable


def _new_uuid() -> str:
    return str(uuid_module.uuid4())


def _now_millis() -> int:
    return int(round(time() * 1000))


@dataclass
class CommandForm(Serializable):
    command: str
    path: str
    exit_status: int
    process_id: int
    process_start_time: int
    uuid: str = field(default_factory=_new_uuid)
    created: int = field(default_factory=_now_millis)

    def __post_init__(self) -> None:
        self.process_id = int(self.process_id)
