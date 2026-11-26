import pytest
import mano_file
from cpu_documents import read


def unexpected_restore(payload):
    pytest.fail("Draft must not be assembled or restored")


@pytest.mark.parametrize("source", ["", "incomplete !", "HLT\n; توضیح\n", "  ORG 100\n\n"])
def test_draft_exact_round_trip(tmp_path, source):
    path = tmp_path / "draft.mano"
    mano_file.save(path, "asm", source)
    assert read(path, unexpected_restore) == ("asm", source)


def test_session_delegates_to_validator(tmp_path):
    path = tmp_path / "cpu.mano"
    payload = {"source": "HLT"}
    mano_file.save(path, "cpu-run", payload)
    marker = object()
    def restore(value):
        assert value == payload
        return marker
    assert read(path, restore) == ("cpu-run", marker)


def test_rejected_session_propagates(tmp_path):
    path = tmp_path / "cpu.mano"
    mano_file.save(path, "cpu-run", {})
    def restore(value):
        raise ValueError("Invalid checkpoint")
    with pytest.raises(ValueError, match="Invalid checkpoint"):
        read(path, restore)


@pytest.mark.parametrize("kind,payload", [("rtl", "AC ← 0"), ("state-run", {}), ("circuit", {})])
def test_wrong_kind(tmp_path, kind, payload):
    path = tmp_path / "wrong.mano"
    mano_file.save(path, kind, payload)
    with pytest.raises(ValueError):
        read(path, unexpected_restore)


def test_malformed_and_missing(tmp_path):
    path = tmp_path / "bad.mano"
    with pytest.raises(OSError):
        read(path, unexpected_restore)
    path.write_text('{"format":"mano-studio","version":1,"version":1,"kind":"asm","payload":"HLT"}')
    with pytest.raises(ValueError):
        read(path, unexpected_restore)
