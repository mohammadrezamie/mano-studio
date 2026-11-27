import copy
import xml.etree.ElementTree as ET

import pytest
from ci_junit import junit_key, verify_junit


NODES = ["tests/test_demo.py::test_a[RTL::A[0]]", "tests/test_demo.py::TestB::test_b"]


@pytest.fixture
def evidence(tmp_path):
    report = dict(selected=NODES, terminal={NODES[0]: "passed", NODES[1]: "skipped"},
                  duration_ms={NODES[0]: 42, NODES[1]: 1})
    suite = ET.Element("testsuite", tests="2", errors="0", failures="0", skipped="1")
    for node, seconds in zip(NODES, ("0.042", "0.001")):
        cls, name = junit_key(node)
        case = ET.SubElement(suite, "testcase", classname=cls, name=name, time=seconds)
        if node == NODES[1]:
            ET.SubElement(case, "skipped")
    path = tmp_path / "report.xml"
    return report, suite, path


def test_identity():
    assert junit_key(NODES[0]) == ("tests.test_demo", "test_a[RTL::A[0]]")
    assert junit_key(NODES[1]) == ("tests.test_demo.TestB", "test_b")


def test_valid(evidence):
    report, suite, path = evidence
    ET.ElementTree(suite).write(path)
    assert verify_junit(path, report) == {"tests": 2, "skipped": 1}


@pytest.mark.parametrize("damage", ["missing", "extra", "duplicate", "wrong-name", "failure",
    "error", "outcome", "duration", "nan", "skip-count", "total", "missing-terminal"])
def test_bad_evidence(evidence, damage):
    report, suite, path = evidence
    case = suite[0]
    if damage == "missing":
        suite.remove(case)
    elif damage in ("extra", "duplicate"):
        extra = copy.deepcopy(case)
        if damage == "extra":
            extra.set("name", "unexpected")
        suite.append(extra)
    elif damage == "wrong-name":
        case.set("name", "wrong")
    elif damage in ("failure", "error"):
        ET.SubElement(case, damage)
    elif damage == "outcome":
        ET.SubElement(case, "skipped")
    elif damage == "duration":
        case.set("time", "1.0")
    elif damage == "nan":
        case.set("time", "nan")
    elif damage == "skip-count":
        suite.set("skipped", "0")
    elif damage == "total":
        suite.set("tests", "1")
    else:
        report["terminal"].pop(NODES[0])
    ET.ElementTree(suite).write(path)
    with pytest.raises(ValueError):
        verify_junit(path, report)
