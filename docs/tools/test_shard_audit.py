import xml.etree.ElementTree as ET
import zipfile

import pytest
from shard_plan import make_plan
from shard_audit import audit


CASES = {("tests.demo", f"test_{i}"): 10 - i for i in range(8)}


def archive(path, rows, bad=None):
    rows = list(rows)
    suite = ET.Element("testsuite", tests=str(len(rows)), failures=str(int(bad == "failure")),
                       errors=str(int(bad == "error")), skipped=str(int(bad == "skipped")))
    for i, (module, name) in enumerate(rows):
        case = ET.SubElement(suite, "testcase", classname=module, name=name, time="1.0")
        if i == 0 and bad:
            ET.SubElement(case, bad)
    with zipfile.ZipFile(path, "w") as z:
        z.writestr("regression.xml", ET.tostring(suite))
    return path


def fixture(tmp_path):
    plan = make_plan(CASES, 4)
    baseline = archive(tmp_path / "baseline.zip", CASES)
    reports = [archive(tmp_path / f"{i}.zip", s["tests"]) for i, s in enumerate(plan["shards"])]
    return plan, baseline, reports


def test_exact_union(tmp_path):
    report = audit(*fixture(tmp_path))
    assert report["regression_evidence_clean"] and report["union_matches_baseline"]
    assert report["same_revision_verified"] is False and report["public_release_approved"] is False


def test_missing_report(tmp_path):
    plan, baseline, reports = fixture(tmp_path)
    with pytest.raises(ValueError):
        audit(plan, baseline, reports[:-1])


def test_swapped_shards(tmp_path):
    plan, baseline, reports = fixture(tmp_path)
    reports[0], reports[1] = reports[1], reports[0]
    result = audit(plan, baseline, reports)
    assert result["union_matches_baseline"] and not result["regression_evidence_clean"]


def test_duplicate_shards(tmp_path):
    plan, baseline, reports = fixture(tmp_path)
    reports[1] = reports[0]
    result = audit(plan, baseline, reports)
    assert not result["regression_evidence_clean"] and result["missing_total"] > 0
    assert result["shards"][1]["duplicates_across_shards"] > 0


@pytest.mark.parametrize("bad", ["failure", "error", "skipped"])
def test_nonpass(tmp_path, bad):
    plan, baseline, reports = fixture(tmp_path)
    archive(reports[0], plan["shards"][0]["tests"], bad)
    result = audit(plan, baseline, reports)
    assert result["union_matches_baseline"] and not result["regression_evidence_clean"]


def test_wrong_serial_revision(tmp_path):
    plan, baseline, reports = fixture(tmp_path)
    archive(baseline, list(CASES)[:-1])
    with pytest.raises(ValueError):
        audit(plan, baseline, reports)
