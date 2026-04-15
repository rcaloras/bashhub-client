from __future__ import annotations

import json
from typing import Any, Callable, TypeVar, cast

import inflection
import jsonpickle

T = TypeVar('T', bound='Serializable')


class Serializable(object):
    def to_JSON(self) -> str:
        underscores = jsonpickle.encode(self)
        temp = json.loads(underscores)
        camel_case = self.convert_json(temp, self.lower_camelize)
        return cast(str, jsonpickle.encode(camel_case))

    @classmethod
    def lower_camelize(cls, string: str) -> str:
        return inflection.camelize(string, False)

    @classmethod
    def convert_json(
        cls, d: dict[str, Any], convert: Callable[[str], str]
    ) -> dict[str, Any]:
        new_d = {}
        for k, v in d.items():
            new_d[convert(k)] = cls.convert_json(v, convert) if isinstance(
                v, dict) else v
        return new_d

    @classmethod
    def from_JSON(cls: type[T], response: str) -> T:
        temp_camel_case = json.loads(response)
        temp = cls.convert_json(temp_camel_case, inflection.underscore)

        # Add back our python classname so jsonpickle
        # knows what class to deserialize it as
        class_name = cls.__module__ + '.' + cls.__name__
        temp['py/object'] = class_name

        pickle = json.dumps(temp)
        return cast(T, jsonpickle.decode(pickle))

    @classmethod
    def from_JSON_list(cls: type[T], response: list[Any]) -> list[T]:

        #response = json.load(response)

        # Use list comprehension to map every json object
        # back to its object with from_JSON
        items = [cls.from_JSON(json.dumps(item)) for item in response]
        return items
