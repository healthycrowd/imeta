import json
from pathlib import Path
from tempfile import NamedTemporaryFile, TemporaryDirectory
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


def json_file(name):
    return str(Path(__file__).parents[0] / "json" / f"{name}")


def test_from_dict_success():
    metadata = ImageMetadata(VALID_METADATA_V1)
    assert_deserialized(VALID_METADATA_V1, metadata)


def test_from_str_success():
    metadata = ImageMetadata.from_str(json.dumps(VALID_METADATA_V1))
    assert_deserialized(VALID_METADATA_V1, metadata)


def test_from_file_success():
    metadata = ImageMetadata.from_file(json_file("valid_v1.json"))
    assert_deserialized(VALID_METADATA_V1, metadata)


def test_from_image_success():
    metadata = ImageMetadata.from_image(json_file("valid_v1.jpg"))
    assert_deserialized(VALID_METADATA_V1, metadata)


def test_to_dict_success():
    metadata = ImageMetadata(VALID_METADATA_V1)
    data = dict(metadata)
    assert data == VALID_METADATA_V1


def test_to_str_success():
    metadata = ImageMetadata(VALID_METADATA_V1)
    data_str = str(metadata)
    assert data_str == json.dumps(VALID_METADATA_V1)


def test_to_file_success():
    metadata = ImageMetadata(VALID_METADATA_V1)
    tofile = NamedTemporaryFile()
    metadata.to_file(tofile.name)

    filepath = Path(tofile.name)
    data_str = filepath.read_text()
    assert data_str == json.dumps(VALID_METADATA_V1)


def test_to_image_success():
    metadata = ImageMetadata(VALID_METADATA_V1)
    tmpdir = TemporaryDirectory()
    topath = Path(tmpdir.name)
    metadata.to_image(str(topath / "test.jpg"))

    data_str = (topath / "test.json").read_text()
    assert data_str == json.dumps(VALID_METADATA_V1)


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


def test_success_for_image():
    filename = "test/file.jpg"
    metaname = ImageMetadata.for_image(filename)
    assert metaname == "test/file.json"


def test_file_success_unicode():
    metadata_dict = VALID_METADATA_V1.copy()
    metadata_dict["source_name"] = "<Imagé *>"
    metadata = ImageMetadata(metadata_dict)
    tmpdir = TemporaryDirectory()
    topath = Path(tmpdir.name)
    tofile = str(topath / "test.json")

    metadata.to_file(tofile)
    metadata = ImageMetadata.from_file(tofile)

    actual_metadata = dict(metadata)
    assert actual_metadata == metadata_dict
    data_str = Path(tofile).read_bytes()
    assert metadata_dict["source_name"].encode() in data_str
