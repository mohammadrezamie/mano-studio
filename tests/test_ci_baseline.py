import pytest
from ci_baseline import identity_digest, verify_baseline

OLD = ["tests/test_original.py::test_example[a]", "tests/test_original.py::test_example[b]"]
NEW = ["tests/test_ci_shard.py::test_x", "tests/test_ci_junit.py::test_x",
       "tests/test_ci_baseline.py::test_x"]
DIGEST = identity_digest([("tests.test_original", "test_example[a]"),
                          ("tests.test_original", "test_example[b]")])


def test_baseline_identity():
    assert verify_baseline(OLD + NEW, 2, DIGEST) == 2


@pytest.mark.parametrize("nodes", [OLD[:1] + NEW, OLD + NEW[:2],
    OLD + NEW + [OLD[0]], [OLD[0], OLD[1].replace("[b]", "[c]")] + NEW])
def test_reject_membership_changes(nodes):
    with pytest.raises(ValueError):
        verify_baseline(nodes, 2, DIGEST)
