import jsonpickle
import json
import requests

class Serializable(object):
  def to_JSON(self):
    return jsonpickle.encode(self.wrapped)

  @classmethod
  def from_JSON(cls, response):
    temp = json.loads(response)

    # Add back our python classname so jsonpickle
    # knows what class to deserialize it as
    class_name = cls.__module__ + '.' + cls.__name__
    temp['py/object'] = class_name

    pickle = json.dumps(temp)
    return jsonpickle.decode(pickle)


  @classmethod
  def from_JSON_list(cls, response):
    # Use list comprehension to map every json object
    # back to its object with from_JSON
    items = [cls.from_JSON(json.dumps(item)) for item in response]
    return items
