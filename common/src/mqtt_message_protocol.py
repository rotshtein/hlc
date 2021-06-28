import json
from typing import Optional


class Message:

    def __init__(self, message: Optional[str] = ''):
        self.message = message

    def toJson(self) -> str:
        return json.dumps(self.__dict__, default=lambda o: o.__dict__)

    def fromJson(self, json_object: json) -> object:
        self.message = json_object
        return self

    def fromByteArray(self, json_array: bytearray) -> object:
        j = json.loads(json_array.decode('utf-8'))
        return self.fromJson(j)

    def getMessage(self) -> str:
        return self.message

    def to_string(self) -> str:
        return ("Message = %s" % (self.message))
