import json
from jsonschema import validate

from .schema import Schema
from .serializer import Serializer
from .exceptions import ValidationError


__version__ = "0.1.0"


class ImageMetadata:
    def __init__(self, data):
        if not isinstance(data, dict) or "$version" not in data:
            raise ValidationError(
                "Image metadata must contain a top-level $version key"
            )

        self._schema = Schema.get(data["$version"])
        self._serializer = Serializer.get(data["$version"])
        print(data)
        print(Serializer._SERIALIZERS)
        if not self._schema or not self._serializer:
            raise ValidationError(
                f"data['$version'] is not a supported image metadata version"
            )

        validate(instance=data, schema=self._schema)
        self._serializer.deserialize(data, self)

    @classmethod
    def from_str(cls, data_str):
        data = json.loads(data_str)
        return cls(data)

    @classmethod
    def from_file(cls, filename):
        with open(filename, "r") as fh:
            data_str = fh.read()
        return cls.from_str(data_str)

    def __str__(self):
        data = self._serializer.serialize(self)
        data_str = json.dumps(data)
        return data_str

    def to_file(self, filename):
        data_str = str(self)
        with open(filename, "w") as fh:
            fh.write(data_str)