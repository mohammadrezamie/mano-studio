"""Measured scheduling hints only; never a test selection or release gate."""
import hashlib
import json
from pathlib import Path


def read_profile(path):
    raw = Path(path).read_bytes()
    value = json.loads(raw)
    if not isinstance(value, dict) or value.get("schema") != 1:
        raise ValueError("Unknown timing profile")
    for field in ("weights_ms", "file_defaults_ms"):
        mapping = value.get(field)
        if not isinstance(mapping, dict) or any(
            not isinstance(k, str) or not k or type(v) is not int or v < 1
            for k, v in mapping.items()
        ):
            raise ValueError("Invalid timing weights")
    if type(value.get("default_ms")) is not int or value["default_ms"] < 1:
        raise ValueError("Invalid timing default")
    return value, hashlib.sha256(raw).hexdigest()


def estimate(nodeid, profile):
    file_name = nodeid.split("::", 1)[0]
    family = nodeid.split("[", 1)[0]
    return profile["weights_ms"].get(nodeid, profile["weights_ms"].get(family,
           profile["file_defaults_ms"].get(file_name, profile["default_ms"])))


def weighted_partition(nodeids, count, profile):
    """Longest estimated test first, assigned to least estimated work."""
    if count < 1 or len(nodeids) != len(set(nodeids)):
        raise ValueError("Invalid shard count or duplicate collection")
    loads = [0] * count
    shards = [[] for _ in range(count)]
    order = sorted(nodeids, key=lambda n: (-estimate(n, profile),
                   hashlib.sha256(n.encode("utf-8")).digest(), n))
    for nodeid in order:
        index = min(range(count), key=lambda i: (loads[i], len(shards[i]), i))
        shards[index].append(nodeid)
        loads[index] += estimate(nodeid, profile)
    return [sorted(shard) for shard in shards]


def observed_profile(reports, source, platform, previous):
    """Export exact observed totals for review; do not mutate input hints."""
    durations = {}
    for report in reports:
        for node, ms in report["duration_ms"].items():
            if node in durations:
                raise ValueError("Duplicate observed timing")
            durations[node] = max(1, ms)
    return {"schema": 1, "source": source, "platform": platform,
            "sample_count": len(durations), "default_ms": previous["default_ms"],
            "file_defaults_ms": previous["file_defaults_ms"], "weights_ms": durations}
