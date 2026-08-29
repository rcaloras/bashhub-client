"""Tests for the dataclass-based Serializable base.

These cover the parsing contract shared by every model: camelCase on the
wire, snake_case in Python, unknown server fields ignored, and malformed
responses failing here rather than downstream.
"""
import json

import pytest

from bashhub.model import (
    Command,
    CommandForm,
    LoginForm,
    LoginResponse,
    MinCommand,
    RegisterSystem,
    RegisterUser,
    StatusView,
    System,
    SystemPatch,
)

# A real GET /api/v1/command/<uuid> response body.
COMMAND_RESPONSE = json.dumps({
    "uuid": "4e7860d4-19e7-4e72-9bf5-f76f3f78d60d",
    "command": "vim bashhub/model/min_command.py",
    "path": "/home/elementz/git/bashhub-client",
    "created": 1438653799957,
    "exitStatus": 0,
    "username": "rccola",
    "systemName": "Kashmir",
    "sessionId": "55c00b6ae4b0e2abc9bc0da1",
})


class TestKeyConversion:
    def test_camel_case_response_maps_to_snake_case_attributes(self):
        command = Command.from_JSON(COMMAND_RESPONSE)
        assert command.system_name == "Kashmir"
        assert command.session_id == "55c00b6ae4b0e2abc9bc0da1"
        assert command.exit_status == 0

    def test_snake_case_attributes_serialize_back_to_camel_case(self):
        payload = json.loads(
            RegisterSystem("home", "aa:bb", "myhost", "3.1.0").to_JSON())
        assert payload == {
            "name": "home",
            "mac": "aa:bb",
            "hostname": "myhost",
            "clientVersion": "3.1.0",
        }

    def test_round_trip_preserves_every_field(self):
        command = Command.from_JSON(COMMAND_RESPONSE)
        assert Command.from_JSON(command.to_JSON()) == command


class TestUnknownFields:
    def test_unknown_server_fields_are_ignored(self):
        """A field added server-side must not break an older client."""
        body = json.loads(COMMAND_RESPONSE)
        body["someBrandNewField"] = "surprise"
        command = Command.from_JSON(json.dumps(body))
        assert command.command == "vim bashhub/model/min_command.py"
        assert not hasattr(command, "some_brand_new_field")

    def test_jsonpickle_directives_are_inert_data(self):
        """Responses are parsed as plain JSON, never reconstructed as objects.

        The previous jsonpickle-based implementation honoured py/reduce in a
        response body, which executed the named callable during parsing."""
        body = json.loads(COMMAND_RESPONSE)
        body["evil"] = {
            "py/reduce": [{"py/function": "os.getcwd"}, {"py/tuple": []}]
        }
        command = Command.from_JSON(json.dumps(body))
        assert not hasattr(command, "evil")
        assert command.username == "rccola"

    def test_py_object_key_does_not_select_a_class(self):
        body = json.loads(COMMAND_RESPONSE)
        body["py/object"] = "bashhub.model.system.System"
        assert isinstance(Command.from_JSON(json.dumps(body)), Command)


class TestMalformedResponses:
    def test_missing_required_field_raises_at_the_parse_boundary(self):
        with pytest.raises(ValueError, match="Command"):
            Command.from_JSON('{"command":"ls","uuid":"abc"}')

    @pytest.mark.parametrize("body", ['[1,2,3]', '"a string"', 'null', '42'])
    def test_non_object_body_raises_value_error(self, body):
        with pytest.raises(ValueError, match="expected a JSON object"):
            Command.from_JSON(body)

    def test_from_JSON_list_rejects_a_non_list(self):
        with pytest.raises(ValueError, match="expected a JSON array"):
            MinCommand.from_JSON_list({"detail": "an error body"})

    def test_from_JSON_list_parses_each_item(self):
        commands = MinCommand.from_JSON_list([
            {"command": "ls", "created": 1, "uuid": "a"},
            {"command": "cd", "created": 2, "uuid": "b"},
        ])
        assert [c.command for c in commands] == ["ls", "cd"]


class TestOptionalFields:
    def test_absent_optional_field_defaults_to_none(self):
        body = json.loads(COMMAND_RESPONSE)
        del body["exitStatus"]
        assert Command.from_JSON(json.dumps(body)).exit_status is None

    def test_explicit_null_optional_field_is_none(self):
        body = json.loads(COMMAND_RESPONSE)
        body["systemName"] = None
        body["sessionId"] = None
        command = Command.from_JSON(json.dumps(body))
        assert command.system_name is None
        assert command.session_id is None


class TestServerContract:
    """Each response model must parse the shape its endpoint actually returns."""

    def test_system_parses_the_system_endpoint_response(self):
        system = System.from_JSON(
            json.dumps({
                "id": "sys-1",
                "name": "Kashmir",
                "mac": "151965074237064",
                "hostname": "myhost",
                "clientVersion": "3.1.0",
            }))
        assert system.name == "Kashmir"
        assert system.mac == "151965074237064"

    def test_system_parses_response_with_null_optional_fields(self):
        system = System.from_JSON(
            json.dumps({
                "id": "sys-1",
                "name": "Kashmir",
                "mac": "aa:bb",
                "hostname": None,
                "clientVersion": None,
            }))
        assert system.hostname is None
        assert system.client_version is None

    def test_status_view_parses_the_client_view_response(self):
        status = StatusView.from_JSON(
            json.dumps({
                "username": "rccola",
                "totalCommands": 10,
                "totalSessions": 2,
                "totalSystems": 3,
                "totalCommandsToday": 4,
                "sessionName": "1234",
                "sessionStartTime": 1438653799957,
                "sessionTotalCommands": 5,
            }))
        assert status.total_commands_today == 4
        assert status.session_total_commands == 5

    def test_login_response_parses_access_token(self):
        assert LoginResponse.from_JSON(
            '{"accessToken":"tok"}').access_token == "tok"


class TestOutgoingPayloads:
    """Request bodies must keep the exact shape the server validates."""

    def test_command_form_payload(self):
        payload = json.loads(
            CommandForm("ls -la", "/tmp", 0, 123, 1438653798957).to_JSON())
        assert payload["command"] == "ls -la"
        assert payload["exitStatus"] == 0
        assert payload["processId"] == 123
        assert payload["processStartTime"] == 1438653798957
        assert payload["uuid"] and payload["created"]

    def test_command_form_coerces_process_id_to_int(self):
        assert CommandForm("ls", "/tmp", 0, "4321", 1).process_id == 4321

    def test_command_form_generates_a_unique_uuid_per_instance(self):
        first = CommandForm("ls", "/tmp", 0, 1, 1)
        second = CommandForm("ls", "/tmp", 0, 1, 1)
        assert first.uuid != second.uuid

    def test_register_user_payload_includes_default_registration_code(self):
        payload = json.loads(RegisterUser("a@b.c", "user", "pw").to_JSON())
        assert payload == {
            "email": "a@b.c",
            "username": "user",
            "password": "pw",
            "registrationCode": "",
        }

    def test_login_form_payload_omits_nothing(self):
        assert json.loads(LoginForm("user", "pw").to_JSON()) == {
            "username": "user",
            "password": "pw",
            "mac": None,
        }


class TestModelHelpers:
    def test_to_min_command_carries_the_display_fields(self):
        command = Command.from_JSON(COMMAND_RESPONSE)
        min_command = command.to_min_command()
        assert min_command.command == command.command
        assert min_command.created == command.created
        assert min_command.uuid == command.uuid

    def test_min_command_str_is_the_command_text(self):
        assert str(MinCommand("ls -la", 1, "u")) == "ls -la"

    def test_system_str_is_name_and_id(self):
        assert str(System("Kashmir", "aa:bb", "sys-1")) == "Kashmir sys-1"

    def test_system_patch_str_handles_unset_fields(self):
        assert str(SystemPatch(hostname="h")) == " "
