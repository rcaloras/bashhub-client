from time import *
import uuid
from .serializable import Serializable


class CommandForm(Serializable):
    def __init__(self, command, path, exit_status, process_id,
                 process_start_time):
        self.uuid = uuid.uuid4().__str__()
        self.command = command
        self.path = path
        self.exit_status = exit_status
        self.process_id = int(process_id)
        self.process_start_time = process_start_time
        self.created = int(round(time() * 1000))
