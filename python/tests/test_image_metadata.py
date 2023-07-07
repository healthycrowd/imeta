import json
import pytest

from imeta import ImageMetadata
from imeta.exceptions import ValidationError, ValidationErrors

VALID_METADATA_V1 = {
    "$version": "1.0",
    "source_url": "https://github.com",
    "source_id": "1",
    "source_name": "GitHub",
    "access_date": 1688687306,
    "tags": ["logo", "github"],
}


def assert_deserialized(data, metadata):
    for key in data:
        if key != "$version":
            assert getattr(metadata, key) == data[key]


def test_from_dict_success():
    metadata = ImageMetadata(VALID_METADATA_V1)
    assert_deserialized(VALID_METADATA_V1, metadata)


def test_from_str_success():
    metadata = ImageMetadata.from_str(json.dumps(VALID_METADATA_V1))
    assert_deserialized(VALID_METADATA_V1, metadata)


def test_from_file_success():
    pass


def test_to_dict_success():
    metadata = ImageMetadata(VALID_METADATA_V1)
    data = dict(metadata)
    assert data == VALID_METADATA_V1


def test_to_str_success():
    metadata = ImageMetadata(VALID_METADATA_V1)
    data_str = str(metadata)
    assert data_str == json.dumps(VALID_METADATA_V1)


def test_to_file_success():
    pass


def test_success_minimal():
    data = {"$version": "1.0"}
    metadata = ImageMetadata(data)
    assert_deserialized(data, metadata)


def test_success_additional_properties():
    data = {
        "$version": "1.0",
        "extra": "value",
    }
    metadata = ImageMetadata(data)
    new_data = dict(metadata)
    assert new_data["extra"] == data["extra"]


def test_success_unchanged():
    metadata = ImageMetadata(VALID_METADATA_V1)
    new_data = dict(metadata)
    assert new_data == VALID_METADATA_V1


def test_fail_no_version():
    with pytest.raises(ValidationError):
        ImageMetadata({})


def test_fail_invalid_version():
    with pytest.raises(ValidationError):
        ImageMetadata({"$version": "nope"})


def test_fail_invalid_data():
    with pytest.raises(ValidationErrors):
        ImageMetadata(
            {
                "$version": "1.0",
                "source_url": False,
            }
        )
