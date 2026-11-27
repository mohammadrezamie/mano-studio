import json
import xml.etree.ElementTree as ET

import pytest
from ci_calibrate import calibrate
from ci_junit import junit_key
from ci_shard import partition


def make_reports(root):
    nodes = sorted(f"tests/test_demo.py::test_case[{i}]" for i in range(8))
    for i, selected in enumerate(partition(nodes, 4)):
        folder = root / f"shard-ubuntu-latest-{i}"
        folder.mkdir()
        report = dict(index=i, count=4, source="a"*40, platform="linux", python="3.12",
                      dependencies=["pytest==8"], collected=nodes, selected=selected,
                      terminal=dict.fromkeys(selected, "passed"), exit=0)
        (folder / "shard.json").write_text(json.dumps(report), encoding="utf-8")
        suite = ET.Element("testsuite", tests=str(len(selected)), errors="0", failures="0", skipped="0")
        for node in selected:
            cls, name = junit_key(node)
            ET.SubElement(suite, "testcase", classname=cls, name=name, time="0.150")
        ET.ElementTree(suite).write(folder / "regression.xml")


def test_complete_profile(tmp_path):
    make_reports(tmp_path)
    p = calibrate(tmp_path, "ubuntu-latest", "linux", "a"*40, 4)
    assert p["sample_count"] == 8
    assert p["weights_ms"] == {"tests/test_demo.py::test_case": 150}
    assert len(p["evidence_sha256"]) == 8


def test_missing_report_rejected(tmp_path):
    make_reports(tmp_path)
    (tmp_path / "shard-ubuntu-latest-2" / "shard.json").unlink()
    with pytest.raises(ValueError):
        calibrate(tmp_path, "ubuntu-latest", "linux", "a"*40, 4)


def test_wrong_source_rejected(tmp_path):
    make_reports(tmp_path)
    with pytest.raises(ValueError):
        calibrate(tmp_path, "ubuntu-latest", "linux", "b"*40, 4)
