import json
from pathlib import Path
import shutil
import pytest
from installer.qt_imageformats_notices import collect, EXPECTED, FILES

SOURCE = Path(__file__).resolve().parents[1] / "installer" / "licenses" / "qtimageformats"

def test_collects_exact_upstream_notices_and_keeps_review_open(tmp_path):
    target = tmp_path / "notices"
    result = collect(SOURCE, target)
    assert {row["file"] for row in result["files"]} == set(FILES)
    assert result["review_complete"] is False
    assert result["exact_corresponding_source_verified"] is False
    assert result["redistribution_approved"] is False
    manifest = json.loads((target / "SUPPLEMENT.json").read_text())
    for name, expected in EXPECTED.items():
        row = next(item for item in manifest["files"] if item["file"] == name)
        assert row["sha256"] == expected

def test_rejects_changed_upstream_license_text(tmp_path):
    source = tmp_path / "source"
    shutil.copytree(SOURCE, source)
    (source / "libtiff.txt").write_text("changed")
    with pytest.raises(ValueError, match="license text changed"):
        collect(source, tmp_path / "target")

def test_rejects_missing_attribution(tmp_path):
    source = tmp_path / "source"
    shutil.copytree(SOURCE, source)
    (source / "libwebp-attribution.json").unlink()
    with pytest.raises(ValueError, match="Missing"):
        collect(source, tmp_path / "target")
