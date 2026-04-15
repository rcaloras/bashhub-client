from __future__ import annotations

import uuid
from time import time

from .serializable import Serializable


class CommandForm(Serializable):
    def __init__(self, command: str, path: str, exit_status: int,
                 process_id: int, process_start_time: int) -> None:
        self.uuid = uuid.uuid4().__str__()
        self.command = command
        self.path = path
        self.exit_status = exit_status
        self.process_id = int(process_id)
        self.process_start_time = process_start_time
        self.created = int(round(time() * 1000))
