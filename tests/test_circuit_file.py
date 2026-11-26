import pytest
from circuit_file import MAX_BYTES, read_text


def test_utf8_roundtrip(tmp_path):
    path = tmp_path / "circuit.json"
    content = '{"title":"آزمایش"}\n'
    path.write_bytes(content.encode("utf-8"))
    assert read_text(path) == content


def test_exact_byte_limit(tmp_path):
    path = tmp_path / "large.json"
    path.write_bytes(b"a" * MAX_BYTES)
    assert len(read_text(path)) == MAX_BYTES
    path.write_bytes(b"a" * (MAX_BYTES + 1))
    with pytest.raises(ValueError, match="too large"):
        read_text(path)


def test_bad_utf8_and_missing_file(tmp_path):
    path = tmp_path / "invalid.json"
    path.write_bytes(b"\xff")
    with pytest.raises(UnicodeError):
        read_text(path)
    with pytest.raises(OSError):
        read_text(tmp_path / "absent.json")
