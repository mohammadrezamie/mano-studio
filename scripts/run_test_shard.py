"""Run a deterministic fraction of the full pytest collection without extra plugins."""
from __future__ import annotations

import argparse
import hashlib
import sys

import pytest


def shard_for(nodeid: str, total: int) -> int:
    digest = hashlib.sha256(nodeid.encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big") % total


class ShardPlugin:
    def __init__(self, shard: int, total: int) -> None:
        self.shard = shard
        self.total = total
        self.selected = 0
        self.collected = 0

    def pytest_collection_modifyitems(self, items) -> None:
        self.collected = len(items)
        selected = [item for item in items if shard_for(item.nodeid, self.total) == self.shard]
        self.selected = len(selected)
        items[:] = selected

    def pytest_terminal_summary(self, terminalreporter, exitstatus, config) -> None:
        terminalreporter.write_sep(
            "=",
            f"Mano deterministic shard {self.shard + 1}/{self.total}: "
            f"{self.selected} selected from {self.collected} collected",
        )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--shard", type=int, required=True, help="Zero-based shard index")
    parser.add_argument("--total", type=int, default=10)
    parser.add_argument("--junitxml", required=True)
    args = parser.parse_args()
    if args.total < 1 or not 0 <= args.shard < args.total:
        parser.error("--shard must be in [0, --total)")
    plugin = ShardPlugin(args.shard, args.total)
    return int(
        pytest.main(
            ["-q", "--durations=25", f"--junitxml={args.junitxml}"],
            plugins=[plugin],
        )
    )


if __name__ == "__main__":
    raise SystemExit(main())
