"""Guard the exact previously passing Stable suite while introducing CI-only tests."""
import hashlib
import json
from ci_junit import junit_key

BASELINE_COUNT = 1549
BASELINE_SHA256 = "18094ddecc38cf93d53ee1ac45119ebcb3ba9e99b130a6dc756a6be76e9cff5b"
ADDITIONS = {"tests.test_ci_shard", "tests.test_ci_junit", "tests.test_ci_baseline"}


def identity_digest(keys):
    return hashlib.sha256(json.dumps(sorted(keys), ensure_ascii=True,
                       separators=(",", ":")).encode()).hexdigest()


def verify_baseline(nodeids, expected_count=BASELINE_COUNT, expected_digest=BASELINE_SHA256):
    keys = [junit_key(n) for n in nodeids]
    if len(set(keys)) != len(keys):
        raise ValueError("Duplicate JUnit identity")
    old = [k for k in keys if k[0] not in ADDITIONS]
    if len(old) != expected_count or identity_digest(old) != expected_digest:
        raise ValueError("Previously passing regression membership changed")
    if not ADDITIONS <= {k[0] for k in keys}:
        raise ValueError("Missing new CI contract module")
    return len(old)
