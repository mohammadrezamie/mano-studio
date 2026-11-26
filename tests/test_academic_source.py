from pathlib import Path
import pytest
import academic_source as source


@pytest.fixture
def original(tmp_path, monkeypatch):
    path = tmp_path / "rtl_translator.py"
    path.write_bytes("# آزمایش\r\nprint('RTL')\r\n".encode())
    monkeypatch.setattr(source, "source_path", lambda: path)
    return path


def test_exact_bytes(original, tmp_path):
    target = tmp_path / "copy.py"
    target.write_bytes(b"old content")
    assert source.export_source(target) == target
    assert target.read_bytes() == original.read_bytes() == source.read_source()


@pytest.mark.parametrize("name", ["rtl_translator.py", "copy.txt"])
def test_reject_original_or_wrong_suffix(original, tmp_path, name):
    before = original.read_bytes()
    with pytest.raises(ValueError):
        source.export_source(tmp_path / name)
    assert original.read_bytes() == before
    assert list(tmp_path.iterdir()) == [original]


def test_failed_replace_keeps_file(original, tmp_path, monkeypatch):
    target = tmp_path / "copy.py"
    target.write_bytes(b"previous")
    def fail(*args):
        raise OSError("fixture failure")
    monkeypatch.setattr(source.os, "replace", fail)
    with pytest.raises(OSError):
        source.export_source(target)
    assert target.read_bytes() == b"previous"
    assert set(tmp_path.iterdir()) == {original, target}


def test_packaged_path(tmp_path, monkeypatch):
    monkeypatch.setattr(source.sys, "_MEIPASS", str(tmp_path), raising=False)
    assert source.source_path() == tmp_path / "rtl_translator.py"
