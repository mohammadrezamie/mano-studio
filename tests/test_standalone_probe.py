from installer.standalone_probe import verify_paths
import pytest


def test_private_runtime(tmp_path):
    root = tmp_path / "app"
    root.mkdir()
    module = root / "python314.dll"
    module.touch()
    assert verify_paths(root, {"python": module}, ["python"]) == {"python": "python314.dll"}


def test_outside_and_missing(tmp_path):
    root = tmp_path / "app"
    root.mkdir()
    external = tmp_path / "python314.dll"
    external.touch()
    with pytest.raises(ValueError):
        verify_paths(root, {"python": external}, ["python"])
    with pytest.raises(ValueError):
        verify_paths(root, {}, ["python"])
    with pytest.raises(ValueError):
        verify_paths(root, {"python": root / "missing.dll"}, ["python"])


def test_similar_prefix_is_not_private(tmp_path):
    root = tmp_path / "app"
    root.mkdir()
    sibling = tmp_path / "app-other"
    sibling.mkdir()
    file = sibling / "Qt6Core.dll"
    file.touch()
    with pytest.raises(ValueError):
        verify_paths(root, {"qt": file}, ["qt"])
