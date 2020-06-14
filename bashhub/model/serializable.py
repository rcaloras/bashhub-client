import jsonpickle
import json
import requests
import inflection
from future.utils import iteritems


class Serializable(object):
    def to_JSON(self):
        underscores = jsonpickle.encode(self)
        temp = json.loads(underscores)
        camel_case = self.convert_json(temp, self.lower_camelize)
        return jsonpickle.encode(camel_case)

    @classmethod
    def lower_camelize(cls, string):
        return inflection.camelize(string, False)

    @classmethod
    def convert_json(cls, d, convert):
        new_d = {}
        for k, v in iteritems(d):
            new_d[convert(k)] = cls.convert_json(v, convert) if isinstance(
                v, dict) else v
        return new_d

    @classmethod
    def from_JSON(cls, response):
        temp_camel_case = json.loads(response)
        temp = cls.convert_json(temp_camel_case, inflection.underscore)

        # Add back our python classname so jsonpickle
        # knows what class to deserialize it as
        class_name = cls.__module__ + '.' + cls.__name__
        temp['py/object'] = class_name

        pickle = json.dumps(temp)
        return jsonpickle.decode(pickle)

    @classmethod
    def from_JSON_list(cls, response):

        #response = json.load(response)

        # Use list comprehension to map every json object
        # back to its object with from_JSON
        items = [cls.from_JSON(json.dumps(item)) for item in response]
        return items
