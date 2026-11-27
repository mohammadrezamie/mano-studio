import json
from pathlib import Path
import pytest
from installer.prune_qml import TARGETS, apply, plan


@pytest.fixture
def tree(tmp_path):
    (tmp_path / "ManoStudio.exe").write_bytes(b"exe")
    (tmp_path / "Qt6Core.dll").write_bytes(b"core")
    for relative in TARGETS:
        path = tmp_path / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(relative.encode())
    return tmp_path


def test_prune_exact_unused_qml_group_and_record_hashes(tree):
    report = apply(tree, lambda path: [])
    assert {row["path"] for row in report["targets"]} == TARGETS
    assert report["static_inbound_imports"] == 0
    assert report["dynamic_loading_proven_absent"] is False
    assert report["public_release_approved"] is False
    assert all(not (tree / path).exists() for path in TARGETS)
    assert (tree / "Qt6Core.dll").is_file()
    saved = json.loads((tree / "qt-qml-prune-evidence.json").read_text())
    assert saved == report


def test_retained_binary_dependency_blocks_pruning(tree):
    with pytest.raises(ValueError, match="imports Qt QML/Quick"):
        plan(tree, lambda path: ["Qt6Quick.dll"])
    assert all((tree / path).is_file() for path in TARGETS)


def test_unexpected_qml_binding_blocks_pruning(tree):
    (tree / "_internal" / "PySide6" / "QtQuick.pyd").write_bytes(b"binding")
    with pytest.raises(ValueError, match="Unexpected QML/Quick"):
        plan(tree, lambda path: [])


def test_incomplete_or_changed_group_blocks_pruning(tree):
    (tree / "_internal" / "PySide6" / "Qt6Quick.dll").unlink()
    with pytest.raises(ValueError, match="exact five-library"):
        plan(tree, lambda path: [])


def test_wrong_root(tmp_path):
    with pytest.raises(ValueError, match="Not a frozen"):
        plan(tmp_path, lambda path: [])
