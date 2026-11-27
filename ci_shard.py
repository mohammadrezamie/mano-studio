"""Deterministic pytest sharding and fail-closed aggregate evidence.

Use only for the full, unfiltered regression suite. Every runner collects the
same suite independently; the gate checks exact union, no overlap and outcomes.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest


def partition(nodeids, count):
    if count < 1 or len(nodeids) != len(set(nodeids)):
        raise ValueError("Invalid shard count or duplicate collection")
    ordered = sorted(nodeids, key=lambda n: (hashlib.sha256(n.encode("utf-8")).digest(), n))
    return [sorted(ordered[i::count]) for i in range(count)]


def pytest_addoption(parser):
    parser.addoption("--shard-index", type=int, required=True)
    parser.addoption("--shard-count", type=int, required=True)
    parser.addoption("--shard-report", required=True)


def pytest_configure(config):
    index = config.getoption("--shard-index")
    count = config.getoption("--shard-count")
    if not 0 <= index < count:
        raise pytest.UsageError("Invalid shard index/count")
    config.pluginmanager.register(Shard(config, index, count), "mano-shard-evidence")


class Shard:
    def __init__(self, config, index, count):
        self.config = config
        self.index = index
        self.count = count
        self.collected = []
        self.selected = []
        self.terminal = {}

    @pytest.hookimpl(trylast=True)
    def pytest_collection_modifyitems(self, config, items):
        self.collected = sorted(item.nodeid for item in items)
        self.selected = partition(self.collected, self.count)[self.index]
        wanted = set(self.selected)
        rejected = [item for item in items if item.nodeid not in wanted]
        items[:] = [item for item in items if item.nodeid in wanted]
        if rejected:
            config.hook.pytest_deselected(items=rejected)

    def pytest_runtest_logreport(self, report):
        if report.when == "call" or (report.when == "setup" and report.skipped):
            self.terminal[report.nodeid] = report.outcome

    def pytest_sessionfinish(self, session, exitstatus):
        report = {
            "index": self.index, "count": self.count,
            "source": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
            "platform": sys.platform, "python": sys.version,
            "dependencies": subprocess.check_output([sys.executable, "-m", "pip", "freeze"], text=True).splitlines(),
            "collected": self.collected, "selected": self.selected,
            "terminal": self.terminal, "exit": int(exitstatus),
        }
        Path(self.config.getoption("--shard-report")).write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def verify(reports, count, source, platform):
    if len(reports) != count:
        raise ValueError("Missing or extra shard reports")
    by_index = {r["index"]: r for r in reports}
    if set(by_index) != set(range(count)):
        raise ValueError("Duplicate or missing shard index")
    first = by_index[0]
    collected = first["collected"]
    if not collected:
        raise ValueError("Empty regression collection")
    expected = partition(collected, count)
    observed = []
    for index, report in by_index.items():
        if (report["count"] != count or report["source"] != source or report["platform"] != platform
                or report["exit"] != 0 or report["collected"] != collected
                or report["python"] != first["python"] or report["dependencies"] != first["dependencies"]):
            raise ValueError(f"Inconsistent source, environment, collection or exit: shard {index}")
        if report["selected"] != expected[index] or set(report["terminal"]) != set(expected[index]):
            raise ValueError(f"Incomplete or incorrect execution: shard {index}")
        if any(outcome not in ("passed", "skipped") for outcome in report["terminal"].values()):
            raise ValueError(f"Unexpected test outcome: shard {index}")
        observed.extend(report["selected"])
    if sorted(observed) != collected or len(set(observed)) != len(observed):
        raise ValueError("Incomplete or overlapping regression coverage")
    return {"tests": len(collected), "shards": count,
            "skipped": sum(list(r["terminal"].values()).count("skipped") for r in reports)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--reports", type=Path, required=True)
    parser.add_argument("--count", type=int, required=True)
    parser.add_argument("--source", required=True)
    args = parser.parse_args()
    for os_name, platform in (("ubuntu-latest", "linux"), ("windows-latest", "win32")):
        reports = [json.loads(p.read_text(encoding="utf-8"))
                   for p in sorted(args.reports.glob(f"shard-{os_name}-*/shard.json"))]
        print(os_name, verify(reports, args.count, args.source, platform))


if __name__ == "__main__":
    main()
