import json
from pathlib import Path
from jsonschema.validators import validator_for

from .schema import Schema
from .serializer import Serializer
from .exceptions import ValidationError


__version__ = "1.1.0"


class ImageMetadata:
    def __init__(self, data):
        if not isinstance(data, dict) or "$version" not in data:
            raise ValidationError(
                "Image metadata must contain a top-level $version key"
            )

        self._raw_data = data
        self._schema = Schema.get(data["$version"])
        self._serializer = Serializer.get(data["$version"])
        if not self._schema or not self._serializer:
            raise ValidationError(
                f"data['$version'] is not a supported image metadata version"
            )

        validator = validator_for(self._schema["$schema"])(self._schema)
        validator.check_schema(self._schema)
        validator.validate(data)
        self._serializer.deserialize(data, self)

    @classmethod
    def from_str(cls, data_str):
        data = json.loads(data_str)
        return cls(data)

    @classmethod
    def from_file(cls, filename):
        data_str = Path(filename).read_text()
        return cls.from_str(data_str)

    @classmethod
    def for_image(cls, filename):
        filepath = Path(filename)
        metapath = filepath.parents[0] / f"{filepath.stem}.json"
        return str(metapath)

    @classmethod
    def from_image(cls, filename):
        return cls.from_file(cls.for_image(filename))

    def __iter__(self):
        data = self._serializer.serialize(self)
        data["$version"] = self._serializer._VERSION
        data.move_to_end("$version", last=False)
        for key in self._raw_data.keys():
            if key not in data:
                data[key] = self._raw_data[key]
        return data.items().__iter__()

    def __repr__(self):
        data_str = json.dumps(dict(self))
        return data_str

    def to_file(self, filename):
        data_str = str(self)
        Path(filename).write_text(data_str)

    def to_image(self, filename):
        self.to_file(self.for_image(filename))
