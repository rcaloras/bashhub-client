from __future__ import annotations

import dataclasses
import json
from typing import TYPE_CHECKING, Any, Callable, ClassVar, TypeVar

import inflection

if TYPE_CHECKING:
    from dataclasses import Field

T = TypeVar('T', bound='Serializable')


def _convert_keys(d: dict[str, Any],
                  convert: Callable[[str], str]) -> dict[str, Any]:
    return {convert(k): _convert_value(v, convert) for k, v in d.items()}


def _convert_value(value: Any, convert: Callable[[str], str]) -> Any:
    """Convert keys of any dict reachable from value, including inside lists."""
    if isinstance(value, dict):
        return _convert_keys(value, convert)
    if isinstance(value, list):
        return [_convert_value(item, convert) for item in value]
    return value


def _lower_camelize(string: str) -> str:
    return inflection.camelize(string, False)


class Serializable(object):
    """Base for API models.

    Subclasses are dataclasses whose fields are snake_case; the wire format
    is camelCase. Parsing goes through the dataclass constructor, so a
    response missing a required field fails here rather than surfacing as an
    AttributeError wherever the object is eventually used.
    """

    # Every subclass is a dataclass; declaring this lets mypy accept the
    # dataclasses.asdict/fields calls below on the base type.
    if TYPE_CHECKING:
        __dataclass_fields__: ClassVar[dict[str, Field[Any]]]

    # Set on models representing a partial update, where a field the caller
    # left unset must stay off the wire rather than being sent as null.
    _omit_none: ClassVar[bool] = False

    def to_dict(self) -> dict[str, Any]:
        fields = dataclasses.asdict(self)
        if self._omit_none:
            fields = {k: v for k, v in fields.items() if v is not None}
        return _convert_keys(fields, _lower_camelize)

    def to_JSON(self) -> str:
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls: type[T], data: dict[str, Any]) -> T:
        attributes = _convert_keys(data, inflection.underscore)
        known = {f.name for f in dataclasses.fields(cls)}  # type: ignore[arg-type]
        # Ignore fields the server sends that this client doesn't model, so
        # adding a field server-side stays backwards compatible.
        try:
            return cls(**{k: v for k, v in attributes.items() if k in known})
        except TypeError as error:
            raise ValueError(
                "{0}: could not build from response: {1}".format(
                    cls.__name__, error)) from error

    @classmethod
    def from_JSON(cls: type[T], response: str) -> T:
        data = json.loads(response)
        if not isinstance(data, dict):
            raise ValueError("{0}: expected a JSON object, got {1}".format(
                cls.__name__,
                type(data).__name__))
        return cls.from_dict(data)

    @classmethod
    def from_JSON_list(cls: type[T], response: list[Any]) -> list[T]:
        if not isinstance(response, list):
            raise ValueError("{0}: expected a JSON array, got {1}".format(
                cls.__name__,
                type(response).__name__))
        return [cls.from_dict(item) for item in response]
