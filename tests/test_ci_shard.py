import copy

import pytest

from ci_shard import partition, verify


def reports():
    nodes = [f"tests/test_demo.py::test_case[{i}]" for i in range(19)]
    nodes.sort()
    return [dict(index=i, count=4, source="a"*40, platform="linux",
                 python="3.12", dependencies=["pytest==8"], collected=nodes,
                 selected=selected, terminal=dict.fromkeys(selected, "passed"),
                 duration_ms=dict.fromkeys(selected, 1), profile_sha256=None, exit=0)
            for i, selected in enumerate(partition(nodes, 4))]


def test_partition_is_balanced_and_order_independent():
    nodes = [str(i) for i in range(23)]
    a = partition(nodes, 4)
    assert a == partition(list(reversed(nodes)), 4)
    assert sorted(n for shard in a for n in shard) == sorted(nodes)
    assert max(map(len, a)) - min(map(len, a)) <= 1


def test_reject_duplicate_nodeids():
    with pytest.raises(ValueError):
        partition(["a", "a"], 4)


def test_complete_regression():
    assert verify(reports(), 4, "a"*40, "linux") == dict(tests=19, shards=4, skipped=0)


@pytest.mark.parametrize("damage", ["missing", "duplicate", "source", "platform",
    "dependencies", "python", "collection", "selected", "terminal", "failure", "exit", "duration", "profile"])
def test_aggregate_rejects_bad_evidence(damage):
    r = copy.deepcopy(reports())
    if damage == "missing":
        r.pop()
    elif damage == "duplicate":
        r[-1] = r[0]
    elif damage in ("source", "platform", "python"):
        r[1][damage] = "different"
    elif damage in ("dependencies", "collection", "selected"):
        key = "collected" if damage == "collection" else damage
        r[1][key] = []
    elif damage == "terminal":
        r[1]["terminal"].pop(next(iter(r[1]["terminal"])))
    elif damage == "duration":
        r[1]["duration_ms"].pop(next(iter(r[1]["duration_ms"])))
    elif damage == "profile":
        r[1]["profile_sha256"] = "wrong"
    elif damage == "failure":
        r[1]["terminal"][r[1]["selected"][0]] = "failed"
    else:
        r[1]["exit"] = 1
    with pytest.raises(ValueError):
        verify(r, 4, "a"*40, "linux")


def test_weighted_partition_balances_expensive_nodes():
    from ci_shard_plan import estimate
    nodes = [f"tests/test_big.py::test_{i}" for i in range(20)]
    profile = dict(default_ms=1, file_defaults_ms={}, weights_ms=dict.fromkeys(nodes[:4], 100))
    parts = partition(nodes, 4, profile)
    assert parts == partition(list(reversed(nodes)), 4, profile)
    assert sorted(node for part in parts for node in part) == sorted(nodes)
    loads = [sum(estimate(node, profile) for node in part) for part in parts]
    assert loads == [104] * 4


def test_profile_fallback_and_exact_precedence():
    from ci_shard_plan import estimate
    p = dict(default_ms=2, file_defaults_ms={"tests/test_ui.py": 10},
             weights_ms={"tests/test_ui.py::test_a": 30, "tests/test_ui.py::test_a[x]": 50})
    assert [estimate(n, p) for n in ["tests/test_ui.py::test_a[x]", "tests/test_ui.py::test_a[y]",
            "tests/test_ui.py::test_new", "tests/test_other.py::test_new"]] == [50, 30, 10, 2]


def test_profile_content_validation(tmp_path):
    import json
    from ci_shard_plan import read_profile
    f = tmp_path / "profile.json"
    value = dict(schema=1, default_ms=1, file_defaults_ms={}, weights_ms={"a": 2})
    f.write_text(json.dumps(value))
    assert read_profile(f)[0] == value and len(read_profile(f)[1]) == 64
    value["weights_ms"]["a"] = True
    f.write_text(json.dumps(value))
    with pytest.raises(ValueError):
        read_profile(f)


def test_weighted_aggregate_recomputes_partition_and_exports_observations():
    from ci_shard_plan import observed_profile
    r = reports()
    nodes = r[0]["collected"]
    p = dict(default_ms=1, file_defaults_ms={}, weights_ms={nodes[0]: 120})
    for report, selected in zip(r, partition(nodes, 4, p)):
        report["selected"] = selected
        report["terminal"] = dict.fromkeys(selected, "passed")
        report["duration_ms"] = dict.fromkeys(selected, 15)
        report["profile_sha256"] = "profile"
    assert verify(r, 4, "a"*40, "linux", p, "profile")["tests"] == 19
    assert observed_profile(r, "a"*40, "linux", p)["weights_ms"] == dict.fromkeys(nodes, 15)
    r[0]["duration_ms"][r[0]["selected"][0]] = -1
    with pytest.raises(ValueError):
        verify(r, 4, "a"*40, "linux", p, "profile")
