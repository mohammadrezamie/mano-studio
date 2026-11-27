"""Deterministic pytest sharding and fail-closed aggregate evidence.

Use only for the full, unfiltered regression suite. Every runner collects the
same suite independently; the gate checks exact union, no overlap and outcomes.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

import pytest
from ci_junit import verify_junit
from ci_shard_plan import read_profile, weighted_partition, observed_profile


def partition(nodeids, count, profile=None):
    if profile is not None:
        return weighted_partition(nodeids, count, profile)
    if count < 1 or len(nodeids) != len(set(nodeids)):
        raise ValueError("Invalid shard count or duplicate collection")
    ordered = sorted(nodeids, key=lambda n: (hashlib.sha256(n.encode("utf-8")).digest(), n))
    return [sorted(ordered[i::count]) for i in range(count)]


def pytest_addoption(parser):
    parser.addoption("--shard-index", type=int, required=True)
    parser.addoption("--shard-count", type=int, required=True)
    parser.addoption("--shard-report", required=True)
    parser.addoption("--shard-profile", default=None)


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
        self.duration_ms = {}
        path = config.getoption("--shard-profile")
        self.profile, self.profile_sha = read_profile(path) if path else (None, None)

    @pytest.hookimpl(trylast=True)
    def pytest_collection_modifyitems(self, config, items):
        self.collected = sorted(item.nodeid for item in items)
        self.selected = partition(self.collected, self.count, self.profile)[self.index]
        wanted = set(self.selected)
        rejected = [item for item in items if item.nodeid not in wanted]
        items[:] = [item for item in items if item.nodeid in wanted]
        if rejected:
            config.hook.pytest_deselected(items=rejected)

    def pytest_runtest_logreport(self, report):
        self.duration_ms[report.nodeid] = self.duration_ms.get(report.nodeid, 0) + max(0, round(report.duration * 1000))
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
            "duration_ms": self.duration_ms, "profile_sha256": self.profile_sha,
        }
        Path(self.config.getoption("--shard-report")).write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def verify(reports, count, source, platform, profile=None, profile_sha=None):
    if len(reports) != count:
        raise ValueError("Missing or extra shard reports")
    by_index = {r["index"]: r for r in reports}
    if set(by_index) != set(range(count)):
        raise ValueError("Duplicate or missing shard index")
    first = by_index[0]
    collected = first["collected"]
    if not collected:
        raise ValueError("Empty regression collection")
    expected = partition(collected, count, profile)
    observed = []
    for index, report in by_index.items():
        if (report["count"] != count or report["source"] != source or report["platform"] != platform
                or report["exit"] != 0 or report["collected"] != collected
                or report["python"] != first["python"] or report["dependencies"] != first["dependencies"]
                or report.get("profile_sha256") != profile_sha):
            raise ValueError(f"Inconsistent source, environment, collection or exit: shard {index}")
        if report["selected"] != expected[index] or set(report["terminal"]) != set(expected[index]):
            raise ValueError(f"Incomplete or incorrect execution: shard {index}")
        if any(outcome not in ("passed", "skipped") for outcome in report["terminal"].values()):
            raise ValueError(f"Unexpected test outcome: shard {index}")
        durations = report.get("duration_ms", {})
        if set(durations) != set(expected[index]) or any(type(v) is not int or v < 0 for v in durations.values()):
            raise ValueError(f"Missing or invalid measured durations: shard {index}")
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
    parser.add_argument("--profile", type=Path)
    parser.add_argument("--profile-out", type=Path)
    args = parser.parse_args()
    profile, profile_sha = read_profile(args.profile) if args.profile else (None, None)
    if args.profile_out and profile is None:
        parser.error("--profile-out requires --profile")
    for os_name, platform in (("ubuntu-latest", "linux"), ("windows-latest", "win32")):
        reports = []
        for path in sorted(args.reports.glob(f"shard-{os_name}-*/shard.json")):
            report = json.loads(path.read_text(encoding="utf-8"))
            verify_junit(path.with_name("regression.xml"), report)
            reports.append(report)
        print(os_name, verify(reports, args.count, args.source, platform, profile, profile_sha))
        if args.profile_out:
            args.profile_out.mkdir(parents=True, exist_ok=True)
            output = observed_profile(reports, args.source, platform, profile)
            (args.profile_out / f'{os_name}.json').write_text(json.dumps(output, indent=2, sort_keys=True) + '\n', encoding='utf-8')


if __name__ == "__main__":
    main()
