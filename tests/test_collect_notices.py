from pathlib import Path
import json
import pytest
from installer.collect_notices import collect, notice_path, sha256


class Distribution:
    def __init__(self, name, root, files):
        self.metadata = {"Name": name}
        self.version = "1.2.3"
        self.root = root
        self.files = files

    def locate_file(self, file):
        return self.root / file

    def read_text(self, name):
        return f"Name: {self.metadata['Name']}\nVersion: {self.version}\n" if name == "METADATA" else None


def test_inventory_preserves_relative_notices_and_hashes(tmp_path):
    site = tmp_path / "site"
    paths = ["PySide6-1.dist-info/licenses/a/LICENSE", "PySide6-1.dist-info/licenses/b/LICENSE"]
    for i, rel in enumerate(paths):
        p = site / rel
        p.parent.mkdir(parents=True)
        p.write_text(str(i))
    runtime = tmp_path / "python"
    runtime.mkdir()
    (runtime / "LICENSE.txt").write_text("python license fixture")
    root = tmp_path / "dist"
    root.mkdir()
    (root / "Qt6Core.dll").write_bytes(b"fixture")
    target = root / "third-party-notices"
    r = collect(target, [Distribution("PySide6", site, paths)], runtime, root)
    assert not r["review_complete"]
    assert len(r["packages"][0]["notices"]) == 2
    assert len({n["sha256"] for n in r["packages"][0]["notices"]}) == 2
    assert r["binaries"][0]["sha256"] == sha256(root / "Qt6Core.dll")
    assert (target / r["python_license"]["path"]).is_file()
    assert json.loads((target / "inventory.json").read_text()) == r
    assert r["warnings"]  # Partial fixture is not compliance evidence.


@pytest.mark.parametrize("value", ["../a.dist-info/LICENSE", "/a.dist-info/LICENSE", "C:/a.dist-info/LICENSE", "a.dist-info/METADATA", "x/LICENSE"])
def test_unsafe_or_unrelated_paths_rejected(value):
    assert notice_path(value) is None


def test_missing_notices_reported(tmp_path):
    r = collect(tmp_path / "notices", [Distribution("Shiboken6", tmp_path, ["s.dist-info/LICENSE"])], tmp_path, tmp_path / "absent")
    assert any("Missing listed" in w for w in r["warnings"])
    assert any("Python runtime" in w for w in r["warnings"])
    assert any("No frozen binaries" in w for w in r["warnings"])


def test_duplicate_metadata_rejected(tmp_path):
    with pytest.raises(ValueError, match="Duplicate"):
        collect(tmp_path / "notices", [Distribution("PySide6", tmp_path, []), Distribution("pyside6", tmp_path, [])], tmp_path, tmp_path)


@pytest.mark.parametrize("filename", ["METADATA", "PKG-INFO"])
def test_real_distribution_description_preserved(tmp_path, filename):
    from importlib.metadata import PathDistribution
    site = tmp_path / "PyInstaller-1.dist-info"
    site.mkdir()
    metadata = "Metadata-Version: 2.1\nName: PyInstaller\nVersion: 1\n\nOverview\n========\n:Documentation: https://example.invalid/\n:Code: local\nUnicode: آزمایش\n"
    (site / filename).write_text(metadata, encoding="utf-8", newline="")
    dist = PathDistribution(site)
    target = tmp_path / "notices"
    result = collect(target, [dist], tmp_path, tmp_path / "absent")
    assert result["packages"][0]["name"] == "PyInstaller"
    assert (target / "PyInstaller/METADATA.txt").read_bytes() == metadata.encode("utf-8")
    assert not result["review_complete"]


def test_missing_raw_metadata_fails_closed(tmp_path):
    dist = Distribution("PySide6", tmp_path, [])
    dist.read_text = lambda name: None
    with pytest.raises(ValueError, match="Missing distribution metadata"):
        collect(tmp_path / "notices", [dist], tmp_path, tmp_path / "absent")
