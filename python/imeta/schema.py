import json
from pathlib import Path


class SchemaMeta(type):
    def __new__(cls, *args, **kwargs):
        child = super().__new__(cls, *args, **kwargs)
        child._schemas = cls.load_schemas()
        return child

    @classmethod
    def load_schemas(cls):
        schemas = {}
        schemapath = Path(__file__).parents[0] / "schema"

        for filepath in schemapath.iterdir():
            if filepath.is_file() and filepath.suffix == ".json":
                with open(str(filepath), "r") as fh:
                    data = fh.read()
                schemas[filepath.stem] = json.loads(data)

        if not schemas:
            raise Exception("Unable to locate image metadata schemas")

        return schemas


class Schema(metaclass=SchemaMeta):
    @classmethod
    def get(cls, version):
        return cls._schemas.get(version)
