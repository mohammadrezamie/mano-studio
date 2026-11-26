import copy
import pytest
from shard_plan import identity, make_plan, validate_plan, ShardSelection

CASES = {("tests.test_demo", f"test_{i}"): 10 - i for i in range(10)}


def test_exact_disjoint_and_deterministic():
    plan = make_plan(CASES, 4)
    assert plan == make_plan(dict(reversed(list(CASES.items()))), 4)
    groups = validate_plan(plan, CASES)
    assert sum(map(len, groups)) == len(CASES)
    assert set.union(*groups) == set(CASES)
    assert max(x["historical_seconds"] for x in plan["shards"]) <= 15


@pytest.mark.parametrize("workers", [0, 11, True])
def test_bad_worker_count(workers):
    with pytest.raises(ValueError):
        make_plan(CASES, workers)


def test_duplicate_or_changed_collection():
    plan = make_plan(CASES, 4)
    with pytest.raises(ValueError):
        validate_plan(plan, list(CASES)[:-1])
    with pytest.raises(ValueError):
        validate_plan(plan, list(CASES) + [next(iter(CASES))])
    wrong = copy.deepcopy(plan)
    wrong["shards"][0]["tests"].append(wrong["shards"][1]["tests"][0])
    with pytest.raises(ValueError):
        validate_plan(wrong, CASES)


def test_node_identity():
    assert identity(r"tests/test_a.py::TestA::test_x[a::b]") == ("tests.test_a.TestA", "test_x[a::b]")
    assert identity(r"tests\test_a.py::test_x[\u2190]") == ("tests.test_a", r"test_x[\u2190]")


def test_real_pytest_shard(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    tests = tmp_path / "tests"
    tests.mkdir()
    (tests / "test_demo.py").write_text("\n".join(f"def test_{i}():\n    assert True\n" for i in range(10)))
    plan = make_plan(CASES, 4)
    import xml.etree.ElementTree as ET
    report = tmp_path / "shard.xml"
    result = pytest.main(["-q", "tests", "--junitxml=" + str(report)], plugins=[ShardSelection(plan, 0)])
    assert result == 0
    actual = {(c.get("classname"), c.get("name")) for c in ET.parse(report).iter("testcase")}
    assert actual == {tuple(x) for x in plan["shards"][0]["tests"]}
