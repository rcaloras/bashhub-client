from bashhub.model import CommandForm

command_form_string = '{"command":"vim bashhub/model/min_command.py","path":"/home/elementz/git/bashhub-client","created":1438653799957,"uuid":"4e7860d4-19e7-4e72-9bf5-f76f3f78d60d","exitStatus":0,"processId":1000,"processStartTime":1438653798957}'

command_form = CommandForm.from_JSON(command_form_string)


def setup():
    command_form = CommandForm.from_JSON(command_form_string)


def test_from_json():
    assert command_form.path == '/home/elementz/git/bashhub-client'


def test_to_json():
    command_form.process_id = 200
    to_json_command = CommandForm.from_JSON(CommandForm.to_JSON(command_form))
    assert to_json_command.process_id == 200
