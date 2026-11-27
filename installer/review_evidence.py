"""Recompute pinned Windows candidate review evidence, never approve release."""
import hashlib
import json
import ssl
import sys

from installer.redistribution_gate import audit
from installer.runtime_evidence import scan
from installer.wheel_evidence import pins, validate


def paired(portable, setup, name):
    first, second = portable / name, setup / name
    if not first.is_file() or not second.is_file():
        raise ValueError("Missing review evidence: " + name)
    data = first.read_bytes()
    if data != second.read_bytes():
        raise ValueError("Review evidence copies differ: " + name)
    return data


def canonical(value):
    # Serialize tuples as arrays and distinguish JSON booleans from integers.
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False)


def verify(root, archive, python_version=None, runtime_version=None):
    portable, setup = root / "portable-output", root / "installer" / "output"
    constraints = root / "installer" / "windows-candidate-constraints.txt"
    raw_constraints = paired(portable, setup, constraints.name)
    if raw_constraints != constraints.read_bytes():
        raise ValueError("Review constraints differ from exact source")
    raw_pip = paired(portable, setup, "build-wheel-report.json")
    if raw_pip != (root / "build-wheel-report.json").read_bytes():
        raise ValueError("Review pip report differs from build input")
    expected = {
        "redistribution-preflight.json": audit(archive),
        "runtime-evidence.json": scan(archive, python_version or sys.version.split()[0],
                                      runtime_version or ssl.OPENSSL_VERSION_INFO),
        "wheel-evidence.json": validate(json.loads(raw_pip.decode("utf-8-sig")), pins(constraints)),
    }
    digests = {
        constraints.name: hashlib.sha256(raw_constraints).hexdigest(),
        "build-wheel-report.json": hashlib.sha256(raw_pip).hexdigest(),
    }
    for name, result in expected.items():
        raw = paired(portable, setup, name)
        actual = json.loads(raw.decode("utf-8-sig"))
        if canonical(actual) != canonical(result):
            raise ValueError("Review evidence does not match recomputed result: " + name)
        digests[name] = hashlib.sha256(raw).hexdigest()
    return {
        "redistribution_flags": len(expected["redistribution-preflight.json"]["flags"]),
        "runtime_flags": len(expected["runtime-evidence.json"]["flags"]),
        "wheel_packages": len(expected["wheel-evidence.json"]["packages"]),
        "evidence_sha256": digests,
        "manual_review_required": True,
        "public_release_approved": False,
    }
