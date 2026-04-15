#!/usr/bin/python
from __future__ import annotations

import json
from typing import Any

import requests
from requests import ConnectionError, HTTPError

from .bashhub_globals import BH_AUTH, BH_URL
from .model import Command, LoginResponse, MinCommand, StatusView
from .model.command import LoginForm, RegisterUser
from .model.command_form import CommandForm
from .model.system import RegisterSystem, System, SystemPatch
from .version import __version__

# Build our user agent string
user_agent = 'bashhub/%s' % __version__

base_headers: dict[str, str] = {'User-Agent': user_agent, 'X-Bashhub-version': __version__}

json_headers: dict[str, str] = dict(
    {'content-type': 'application/json',
     'Accept': 'application/json'}, **base_headers)


def _extract_error_message(response: requests.Response, fallback: str) -> str:
    """Return a clean error string from an API response.

    The server sends plain text for 401/409/422 and JSON (DRF format) for
    400. Try plain text first (if it looks usable), then attempt JSON
    extraction, then fall back to the provided generic string."""
    text = response.text.strip() if response.text else ""

    # If the body is plain text (no JSON braces), use it directly.
    if text and not text.startswith("{") and not text.startswith("["):
        return text

    # Try to extract a message from DRF-style JSON:
    # {"field": ["error msg", ...]} or {"detail": "error msg"}
    try:
        data: Any = response.json()
        if isinstance(data, dict):
            if "detail" in data:
                return str(data["detail"])
            # Collect first message from each field
            messages: list[str] = []
            for value in data.values():
                if isinstance(value, list) and value:
                    messages.append(str(value[0]))
                elif isinstance(value, str):
                    messages.append(value)
            if messages:
                return " ".join(messages)
    except Exception:
        pass

    return fallback


def json_auth_headers() -> dict[str, str]:
    return dict({'Authorization': 'Bearer {0}'.format(BH_AUTH())},
                **json_headers)


def base_auth_headers() -> dict[str, str]:
    return dict({'Authorization': 'Bearer {0}'.format(BH_AUTH())},
                **base_headers)


def register_user(register_user: RegisterUser) -> str | None:
    url = BH_URL + "/api/v1/user"
    try:
        response = requests.post(url,
                                 data=register_user.to_JSON(),
                                 headers=json_headers)
        response.raise_for_status()

        # Return our username on a successful response
        return register_user.username

    except ConnectionError:
        print("Looks like there's a connection error. Please try again later")
    except HTTPError:
        if response.status_code in (409, 422):
            print(_extract_error_message(
                response, "Registration failed. Please try again."))
        else:
            print(_extract_error_message(
                response, "Sorry, an unexpected error occurred. Please try again."))
    return None


def login_user(login_form: LoginForm) -> str | None:
    url = BH_URL + "/api/v1/login"
    try:
        response = requests.post(url,
                                 data=login_form.to_JSON(),
                                 headers=json_headers)

        response.raise_for_status()
        login_response_json = json.dumps(response.json())
        return LoginResponse.from_JSON(login_response_json).access_token

    except ConnectionError:
        print("Looks like there's a connection error. Please try again later")
        return None
    except HTTPError:
        if response.status_code == 401:
            print("Incorrect username or password.")
        elif response.status_code == 409:
            print(_extract_error_message(
                response, "Login failed. Please try again."))
        else:
            print(_extract_error_message(
                response, "Sorry, an unexpected error occurred. Please try again."))
        return None


def register_system(register_system: RegisterSystem) -> str | None:
    url = BH_URL + "/api/v1/system"
    try:
        response = requests.post(url,
                                 data=register_system.to_JSON(),
                                 headers=json_auth_headers())
        response.raise_for_status()
        return register_system.name

    except ConnectionError:
        print("Looks like there's a connection error. Please try again later")
    except HTTPError:
        if response.status_code == 409:
            print(_extract_error_message(
                response, "System registration failed. Please try again."))
        else:
            print(_extract_error_message(
                response, "Sorry, an unexpected error occurred. Please try again."))
    return None


def get_system_information(mac: str) -> System | None:
    url = BH_URL + '/api/v1/system'
    payload = {'mac': mac}
    try:
        response = requests.get(url,
                                params=payload,
                                headers=json_auth_headers())
        response.raise_for_status()
        system_json = json.dumps(response.json())
        return System.from_JSON(system_json)
    except ConnectionError:
        print("Looks like there's a connection error. Please try again later")
        return None
    except HTTPError:
        return None


def get_command(uuid: str) -> Command | None:
    url = BH_URL + "/api/v1/command/{0}".format(uuid)
    try:
        response = requests.get(url, headers=json_auth_headers())
        response.raise_for_status()
        json_command = json.dumps(response.json())
        return Command.from_JSON(json_command)

    except ConnectionError:
        print("Looks like there's a connection error. Please try again later")
    except HTTPError as error:
        print(error)
        print("Please try again...")

    return None


def delete_command(uuid: str) -> str | None:
    url = BH_URL + "/api/v1/command/{0}".format(uuid)
    try:
        response = requests.delete(url, headers=base_auth_headers())
        response.raise_for_status()
        return uuid

    except ConnectionError:
        pass
    except HTTPError as error:
        print(error)

    return None


def patch_system(system_patch: SystemPatch, mac: str) -> int | None:

    url = BH_URL + "/api/v1/system/{0}".format(mac)

    r = None
    try:
        r = requests.patch(url,
                           data=system_patch.to_JSON(),
                           headers=json_auth_headers())
        r.raise_for_status()
        return r.status_code
    except Exception:
        if r is not None and r.status_code in (403, 401):
            print("Permissions Issue. Run bashhub setup to re-login.")
        return None


def search(
    limit: int | None = None,
    path: str | None = None,
    query: str | None = None,
    system_name: str | None = None,
    unique: bool | None = None,
    session_id: str | None = None,
) -> list[MinCommand]:

    payload: dict[str, Any] = dict()

    if limit:
        payload["limit"] = limit

    if path:
        payload["path"] = path

    if query:
        payload["query"] = query

    if system_name:
        payload["systemName"] = system_name

    if session_id:
        payload["sessionUuid"] = session_id

    payload["unique"] = str(unique).lower()
    url = BH_URL + "/api/v1/command/search"

    r = None
    try:
        r = requests.get(url, params=payload, headers=json_auth_headers())
        return MinCommand.from_JSON_list(r.json())

    except ConnectionError:
        print("Sorry, looks like there's a connection error. Please try again later")
    except Exception as error:  # noqa: BLE001
        if r is not None:
            if r.status_code in (403, 401):
                print("Permissions Issue. Run bashhub setup to re-login.")
            elif r.status_code in [400]:
                print(
                    "Sorry, an error occurred communicating with Bashhub. Response Code: "
                    + str(r.status_code))
                print(r.text)
            else:
                print(
                    "Sorry, an error occurred communicating with Bashhub. Response Code: "
                    + str(r.status_code))
                print(error)
    return []


def save_command(command: CommandForm) -> None:
    url = BH_URL + "/api/v1/command"

    r = None
    try:
        r = requests.post(url,
                          data=command.to_JSON(),
                          headers=json_auth_headers())
    except ConnectionError:
        print("Sorry, looks like there's a connection error")
        pass
    except Exception:
        if r is not None and r.status_code in (403, 401):
            print("Permissions Issue. Run bashhub setup to re-login.")


def get_status_view(process_id: int, start_time: int) -> StatusView | None:
    url = BH_URL + "/api/v1/client-view/status"

    payload = {'processId': process_id, 'startTime': start_time}
    r = None
    try:
        r = requests.get(url, params=payload, headers=json_auth_headers())
        status_view_json = json.dumps(r.json())
        return StatusView.from_JSON(status_view_json)
    except ConnectionError:
        print("Sorry, looks like there's a connection error")
        return None
    except Exception:  # noqa: BLE001
        if r is not None:
            if r.status_code in (403, 401):
                print("Permissions Issue. Run bashhub setup to re-login.")
            else:
                print(
                    "Sorry, an error occurred communicating with Bashhub. Response Code: "
                    + str(r.status_code))
        return None
