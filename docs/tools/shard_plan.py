"""Opt-in regression sharding pilot; exact collection required, no tests omitted."""
import argparse
import json
import math
from pathlib import Path
import xml.etree.ElementTree as ET
import zipfile

from regression_evidence import load_report


def identity(nodeid):
    head, sep, params = nodeid.partition("[")
    parts = head.split("::")
    if len(parts) < 2 or not parts[0].endswith(".py"):
        raise ValueError("Unsupported pytest node identity")
    module = parts[0][:-3].replace("/", ".").replace("\\", ".")
    return ".".join([module] + parts[1:-1]), parts[-1] + sep + params


def historical_cases(path):
    report, expected = load_report(path)
    if any(report[k] for k in ("failures", "errors", "skipped")):
        raise ValueError("Historical report must be clean")
    with zipfile.ZipFile(path) as archive:
        root = ET.fromstring(archive.read("regression.xml"))
    cases = {(c.get("classname"), c.get("name")): float(c.get("time"))
             for c in root.iter("testcase")}
    if set(cases) != expected:
        raise ValueError("Historical identities changed")
    return cases


def make_plan(cases, workers):
    if type(workers) is not int or not 1 <= workers <= min(32, len(cases)):
        raise ValueError("Invalid worker count")
    for key, seconds in cases.items():
        if (not isinstance(key, tuple) or len(key) != 2 or
                any(not isinstance(x, str) or not x for x in key) or
                not isinstance(seconds, (int, float)) or not math.isfinite(seconds) or seconds < 0):
            raise ValueError("Invalid historical test data")
    buckets = [[] for _ in range(workers)]
    totals = [0.0] * workers
    for key, seconds in sorted(cases.items(), key=lambda row: (-row[1], row[0])):
        index = min(range(workers), key=lambda i: (totals[i], len(buckets[i]), i))
        buckets[index].append(list(key))
        totals[index] += seconds
    return {"format": "mano-regression-shards-v1", "shards": [
        {"tests": rows, "historical_seconds": round(totals[i], 3)}
        for i, rows in enumerate(buckets)]}


def validate_plan(plan, collected):
    if not isinstance(plan, dict) or set(plan) != {"format", "shards"} or plan["format"] != "mano-regression-shards-v1":
        raise ValueError("Invalid shard plan format")
    shards = plan["shards"]
    if not isinstance(shards, list) or not 1 <= len(shards) <= 32:
        raise ValueError("Invalid shard count")
    seen, groups = set(), []
    for shard in shards:
        if not isinstance(shard, dict) or set(shard) != {"tests", "historical_seconds"}:
            raise ValueError("Invalid shard")
        rows = shard["tests"]
        if not isinstance(rows, list) or not rows:
            raise ValueError("Empty shard")
        group = set()
        for row in rows:
            if not isinstance(row, list) or len(row) != 2 or any(not isinstance(x, str) or not x for x in row):
                raise ValueError("Invalid planned identity")
            key = tuple(row)
            if key in seen:
                raise ValueError("Duplicate planned identity")
            seen.add(key)
            group.add(key)
        groups.append(group)
    collected = list(collected)
    if len(collected) != len(set(collected)) or seen != set(collected):
        raise ValueError("Planned and collected identities differ; regenerate for exact revision")
    return groups


class ShardSelection:
    def __init__(self, plan, index):
        self.plan, self.index = plan, index

    def pytest_collection_modifyitems(self, config, items):
        import pytest
        try:
            keys = [identity(item.nodeid) for item in items]
            groups = validate_plan(self.plan, keys)
            if type(self.index) is not int or not 0 <= self.index < len(groups):
                raise ValueError("Invalid shard index")
        except ValueError as exc:
            raise pytest.UsageError(str(exc)) from exc
        selected, rejected = [], []
        for item, key in zip(items, keys):
            (selected if key in groups[self.index] else rejected).append(item)
        items[:] = selected
        config.hook.pytest_deselected(items=rejected)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    plan = commands.add_parser("plan")
    plan.add_argument("report", type=Path)
    plan.add_argument("output", type=Path)
    plan.add_argument("--workers", type=int, default=4)
    run = commands.add_parser("run")
    run.add_argument("plan", type=Path)
    run.add_argument("index", type=int)
    run.add_argument("--junitxml", required=True)
    args = parser.parse_args()
    if args.command == "plan":
        result = make_plan(historical_cases(args.report), args.workers)
        args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        return 0
    import pytest
    result = json.loads(args.plan.read_text(encoding="utf-8"))
    return pytest.main(["-q", "tests", "--junitxml=" + args.junitxml],
                       plugins=[ShardSelection(result, args.index)])


if __name__ == "__main__":
    raise SystemExit(main())
