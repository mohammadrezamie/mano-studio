"""Guard the exact previously passing Stable suite while introducing CI-only tests."""
import hashlib
import json
from ci_junit import junit_key

BASELINE_COUNT = 2218
BASELINE_SHA256 = "07c93f2a2c11423629ff9ba61f436483403514a2e8cfdf1ded9ba424e379e7be"
ADDITIONS = {"tests.test_ci_shard", "tests.test_ci_junit", "tests.test_ci_baseline", "tests.test_capture_lifecycle"}
LIFECYCLE_CASE = ("tests.test_workspace", "test_workspace_disposal_releases_owned_widgets_and_timers")


def identity_digest(keys):
    return hashlib.sha256(json.dumps(sorted(keys), ensure_ascii=True,
                       separators=(",", ":")).encode()).hexdigest()


def verify_baseline(nodeids, expected_count=BASELINE_COUNT, expected_digest=BASELINE_SHA256):
    keys = [junit_key(n) for n in nodeids]
    if len(set(keys)) != len(keys):
        raise ValueError("Duplicate JUnit identity")
    old = [k for k in keys if k[0] not in ADDITIONS and k != LIFECYCLE_CASE]
    if len(old) != expected_count or identity_digest(old) != expected_digest:
        raise ValueError("Previously passing regression membership changed")
    if not ADDITIONS <= {k[0] for k in keys}:
        raise ValueError("Missing new CI contract module")
    if LIFECYCLE_CASE not in keys:
        raise ValueError("Missing workspace disposal contract")
    return len(old)
