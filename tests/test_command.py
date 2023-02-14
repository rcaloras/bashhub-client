from bashhub.model import Command

command_string = '{"command":"vim bashhub/model/min_command.py","path":"/home/elementz/git/bashhub-client","created":1438653799957,"uuid":"4e7860d4-19e7-4e72-9bf5-f76f3f78d60d","exitStatus":0,"username":"rccola","systemName":"Kashmir","sessionId":"55c00b6ae4b0e2abc9bc0da1"}'

no_exit_status_string = '{"command":"vim bashhub/model/min_command.py","path":"/home/elementz/git/bashhub-client","created":1438653799957,"uuid":"4e7860d4-19e7-4e72-9bf5-f76f3f78d60d","username":"rccola","systemName":"Kashmir","sessionId":"55c00b6ae4b0e2abc9bc0da1"}'

command = Command.from_JSON(command_string)


def setup():
    command = Command.from_JSON(command_string)


def test_from_json():
    assert command.path == '/home/elementz/git/bashhub-client'


def test_to_json():
    command.username = 'some-user'
    to_json_command = Command.from_JSON(Command.to_JSON(command))
    assert to_json_command.username == 'some-user'

def test_to_min_command():
    min_command = command.to_min_command()
    assert min_command.command == command.command
    assert min_command.created == command.created
    assert min_command.uuid == command.uuid


def test_no_exit_status():
    no_exit_status = Command.from_JSON(no_exit_status_string)
    assert no_exit_status.exit_status == None
