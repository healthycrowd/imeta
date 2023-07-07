from collections import OrderedDict


class SerializerMeta(type):
    def __new__(cls, *args, **kwargs):
        child = super().__new__(cls, *args, **kwargs)
        if hasattr(child, "_VERSION"):
            child._SERIALIZERS[child._VERSION] = child
        return child


class Serializer(metaclass=SerializerMeta):
    _FIELDS = []
    _SERIALIZERS = {}

    @classmethod
    def get(cls, version):
        return cls._SERIALIZERS.get(version)

    @classmethod
    def deserialize(cls, data, metadata):
        for field in cls._FIELDS:
            setattr(metadata, field, data.get(field))

    @classmethod
    def serialize(cls, metadata):
        data = OrderedDict((field, getattr(metadata, field)) for field in cls._FIELDS)
        return data


class V1Serializer(Serializer):
    _VERSION = "1.0"
    _FIELDS = ["source_url", "source_id", "source_name", "access_date", "tags"]
