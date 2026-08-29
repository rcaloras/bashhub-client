from __future__ import annotations

from dataclasses import dataclass

from .serializable import Serializable


@dataclass
class System(Serializable):
    """A registered system, as returned by GET/POST /api/v1/system.

    hostname/clientVersion are null for systems registered without them."""

    name: str
    mac: str
    id: str
    hostname: str | None = None
    client_version: str | None = None

    def __str__(self) -> str:
        return self.name + " " + self.id


@dataclass
class RegisterSystem(Serializable):
    name: str
    mac: str
    hostname: str
    client_version: str


@dataclass
class SystemPatch(Serializable):
    """A partial update for PATCH /api/v1/system/<mac>.

    Only the fields the caller sets are sent. Every call site names the
    fields it wants to change and leaves the rest alone, so serializing the
    unset ones as null said something the caller never meant."""

    # Unset fields are omitted rather than sent as null.
    _omit_none = True

    name: str | None = None
    mac: str | None = None
    hostname: str | None = None
    client_version: str | None = None

    def __str__(self) -> str:
        return f"{self.name or ''} {self.mac or ''}"
