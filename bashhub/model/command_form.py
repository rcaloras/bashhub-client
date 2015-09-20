from time import *
import uuid
from serializable import Serializable

class CommandForm(Serializable):
    def __init__(self, command, path, exit_status, context):
        self.uuid = uuid.uuid4().__str__()
        self.command = command
        self.path = path
        self.exit_status = exit_status
        self.context = context
        self.created = time()*1000


class UserContext(Serializable):
    def __init__(self, process_id, start_time, user_id, system_id):
        self.process_id = long(process_id)
        self.start_time = start_time
        self.user_id = user_id
        self.system_id = system_id
