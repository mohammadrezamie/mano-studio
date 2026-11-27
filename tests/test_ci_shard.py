import copy

import pytest

from ci_shard import partition, verify


def reports():
    nodes = [f"tests/test_demo.py::test_case[{i}]" for i in range(19)]
    nodes.sort()
    return [dict(index=i, count=4, source="a"*40, platform="linux",
                 python="3.12", dependencies=["pytest==8"], collected=nodes,
                 selected=selected, terminal=dict.fromkeys(selected, "passed"), exit=0)
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
    "dependencies", "python", "collection", "selected", "terminal", "failure", "exit"])
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
    elif damage == "failure":
        r[1]["terminal"][r[1]["selected"][0]] = "failed"
    else:
        r[1]["exit"] = 1
    with pytest.raises(ValueError):
        verify(r, 4, "a"*40, "linux")
