from __future__ import annotations

from .serializable import Serializable


class System(Serializable):
    def __init__(self, name: str, mac: str, id: str, created: int,
                 updated: int, hostname: str, client_version: str) -> None:
        self.name = name
        self.mac = mac
        self.id = id
        self.created = created
        self.updated = updated
        self.hostname = hostname
        self.client_version = client_version

    def __str__(self) -> str:
        return self.name + " " + self.id


class RegisterSystem(Serializable):
    def __init__(self, name: str, mac: str, hostname: str,
                 client_version: str) -> None:
        self.name = name
        self.mac = mac
        self.hostname = hostname
        self.client_version = client_version


class SystemPatch(Serializable):
    def __init__(self,
                 name: str | None = None,
                 mac: str | None = None,
                 hostname: str | None = None,
                 client_version: str | None = None) -> None:
        self.name = name
        self.mac = mac
        self.hostname = hostname
        self.client_version = client_version

    def __str__(self) -> str:
        return f"{self.name or ''} {self.mac or ''}"
