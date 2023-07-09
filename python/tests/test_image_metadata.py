import json
from pathlib import Path
from tempfile import NamedTemporaryFile, TemporaryDirectory
import pytest

from imeta import ImageMetadata
from imeta.exceptions import ValidationError, ValidationErrors


VALID_METADATA_V1 = {
    "source_url": "https://github.com",
    "source_id": "1",
    "source_name": "GitHub",
    "access_date": 1688687306,
    "tags": ["logo", "github"],
    "$version": "1.0",
}
VALID_METADATA_V1_1 = {
    "source_url": "https://github.com",
    "source_id": "1",
    "source_name": "GitHub",
    "access_date": 1688687306,
    "tags": ["logo", "github"],
    "extension": "svg",
    "$version": "1.1",
}
VALID_METADATA_LATEST = VALID_METADATA_V1_1
LATEST_VERSION = "1.1"


def assert_deserialized(data, metadata):
    for key in data:
        if key != "$version":
            assert getattr(metadata, key) == data[key]


def test_from_dict_success():
    metadata = ImageMetadata(VALID_METADATA_LATEST)
    assert_deserialized(VALID_METADATA_LATEST, metadata)


def test_from_str_success():
    metadata = ImageMetadata.from_str(json.dumps(VALID_METADATA_LATEST))
    assert_deserialized(VALID_METADATA_LATEST, metadata)


def test_from_file_success():
    tmpdir = TemporaryDirectory()
    topath = Path(tmpdir.name)
    filepath = Path(topath / "test.json")
    filepath.write_text(json.dumps(VALID_METADATA_LATEST))

    metadata = ImageMetadata.from_file(str(filepath))
    assert_deserialized(VALID_METADATA_LATEST, metadata)


def test_from_image_success():
    tmpdir = TemporaryDirectory()
    topath = Path(tmpdir.name)
    filepath = Path(topath / "test.svg")
    filepath.write_text("testimage")
    Path(topath / "test.json").write_text(json.dumps(VALID_METADATA_LATEST))

    metadata = ImageMetadata.from_image(str(filepath))
    assert_deserialized(VALID_METADATA_LATEST, metadata)


def test_from_image_fail_wrong_extension():
    tmpdir = TemporaryDirectory()
    topath = Path(tmpdir.name)
    filepath = Path(topath / "test.jpg")
    filepath.write_text("testimage")
    Path(topath / "test.json").write_text(json.dumps(VALID_METADATA_LATEST))

    with pytest.raises(ValidationError):
        ImageMetadata.from_image(str(filepath))


def test_from_image_fail_no_image():
    tmpdir = TemporaryDirectory()
    topath = Path(tmpdir.name)
    filepath = Path(topath / "test.jpg")
    Path(topath / "test.json").write_text(json.dumps(VALID_METADATA_LATEST))

    with pytest.raises(ValidationError):
        ImageMetadata.from_image(str(filepath))


def test_to_dict_success():
    metadata = ImageMetadata(VALID_METADATA_LATEST)
    data = dict(metadata)
    assert data == VALID_METADATA_LATEST


def test_to_str_success():
    metadata = ImageMetadata(VALID_METADATA_LATEST)
    data_str = str(metadata)
    assert json.loads(data_str) == VALID_METADATA_LATEST


def test_to_file_success():
    metadata = ImageMetadata(VALID_METADATA_LATEST)
    tofile = NamedTemporaryFile()
    metadata.to_file(tofile.name)

    filepath = Path(tofile.name)
    data_str = filepath.read_text()
    assert json.loads(data_str) == VALID_METADATA_LATEST


def test_to_image_success():
    metadata = ImageMetadata(VALID_METADATA_LATEST)
    tmpdir = TemporaryDirectory()
    topath = Path(tmpdir.name)

    metadata.to_image(str(topath / "test.svg"))

    data_str = (topath / "test.json").read_text()
    assert json.loads(data_str) == VALID_METADATA_LATEST


def test_to_image_fail_wrong_extension():
    metadata = ImageMetadata(VALID_METADATA_LATEST)
    tmpdir = TemporaryDirectory()
    topath = Path(tmpdir.name)

    with pytest.raises(ValidationError):
        metadata.to_image(str(topath / "test.jpg"))


def test_success_minimal():
    data = {"$version": LATEST_VERSION, "extension": "jpg"}
    metadata = ImageMetadata(data)
    assert_deserialized(data, metadata)


def test_success_additional_properties():
    data = {
        "$version": LATEST_VERSION,
        "extension": "jpg",
        "extra": "value",
    }
    metadata = ImageMetadata(data)
    new_data = dict(metadata)
    assert new_data["extra"] == data["extra"]


def test_success_unchanged():
    metadata = ImageMetadata(VALID_METADATA_LATEST)
    new_data = dict(metadata)
    assert new_data == VALID_METADATA_LATEST


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
                "$version": LATEST_VERSION,
                "extension": "jpg",
                "source_url": False,
            }
        )


def test_success_for_image():
    filename = "test/file.jpg"
    metaname = ImageMetadata.for_image(filename)
    assert metaname == "test/file.json"


def test_file_success_unicode():
    metadata_dict = VALID_METADATA_LATEST.copy()
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


def test_success_v1():
    metadata = ImageMetadata(VALID_METADATA_V1)
    tmpdir = TemporaryDirectory()
    topath = Path(tmpdir.name)
    tofile = str(topath / "test.json")

    metadata.to_file(tofile)
    metadata = ImageMetadata.from_file(tofile)

    actual_metadata = dict(metadata)
    assert actual_metadata == VALID_METADATA_V1
