import hashlib
import pytest
from installer.prune_mesa import prune, RELATIVE

DATA = b"test-only Mesa fixture"
DIGEST = hashlib.sha256(DATA).hexdigest()


@pytest.fixture
def frozen(tmp_path):
    (tmp_path / "ManoStudio.exe").write_bytes(b"fake PE")
    target = tmp_path / RELATIVE
    target.parent.mkdir(parents=True)
    target.write_bytes(DATA)
    return tmp_path, target


def test_prune_only_known_file(frozen):
    root, target = frozen
    assert prune(root, lambda p: set(), expected=DIGEST) == [RELATIVE]
    assert not target.exists()
    assert (root / "ManoStudio.exe").exists()
    assert prune(root, lambda p: set(), expected=DIGEST) == []


@pytest.mark.parametrize("mode", ["unknown", "import", "duplicate", "parser"])
def test_reject_without_mutation(frozen, mode):
    root, target = frozen
    digest = DIGEST
    imports = lambda p: set()
    if mode == "unknown":
        digest = "0" * 64
    elif mode == "import":
        imports = lambda p: {"OPENGL32SW.DLL"}
    elif mode == "duplicate":
        (root / "opengl32sw.dll").write_bytes(DATA)
    else:
        def imports(p):
            raise ValueError("invalid PE")
    with pytest.raises(ValueError):
        prune(root, imports, expected=digest)
    assert target.read_bytes() == DATA


def test_reject_nonfrozen(tmp_path):
    with pytest.raises(ValueError):
        prune(tmp_path)
