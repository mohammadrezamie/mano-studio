"""Summarize pytest JUnit timing for developer CI, without runtime dependencies."""
import argparse
from collections import defaultdict
from dataclasses import dataclass
from html import escape
import math
import os
from pathlib import Path
import xml.etree.ElementTree as ET


@dataclass(frozen=True)
class Case:
    module: str
    name: str
    seconds: float
    outcome: str


def read_cases(path):
    root = ET.parse(path).getroot()
    if root.tag not in ('testsuite', 'testsuites'):
        raise ValueError('Expected JUnit testsuite or testsuites')
    cases = []
    for node in root.iter('testcase'):
        seconds = float(node.get('time', '0'))
        if not math.isfinite(seconds) or seconds < 0:
            raise ValueError('Invalid testcase duration')
        outcome = next((kind for kind in ('error', 'failure', 'skipped')
                        if node.find(kind) is not None), 'passed')
        cases.append(Case(node.get('classname', '(unknown)'),
                          node.get('name', '(unnamed)'), seconds, outcome))
    return cases


def label(value):
    return escape(value, quote=False).replace('|', '&#124;').replace('\n', ' ').replace('\r', ' ').replace('`', '&#96;')


def report(cases, limit=25):
    if limit < 1:
        raise ValueError('Limit must be positive')
    total = sum(case.seconds for case in cases)
    counts = defaultdict(int)
    modules = defaultdict(lambda: [0, 0.0])
    for case in cases:
        counts[case.outcome] += 1
        modules[case.module][0] += 1
        modules[case.module][1] += case.seconds
    lines = ['# Pytest timing diagnostics', '',
             f'Cases: {len(cases)} · passed: {counts["passed"]} · failed: {counts["failure"]} · errors: {counts["error"]} · skipped: {counts["skipped"]}',
             f'Sum of reported testcase durations: {total:.3f} s.', '',
             'JUnit durations are not end-to-end job wall time; setup, collection, teardown and runner overhead may differ.',
             'Use these measurements to investigate slow tests, not to remove coverage.', '',
             '## Slowest test modules', '', '| Module | Cases | Seconds | Share |', '|---|---:|---:|---:|']
    for name, (count, seconds) in sorted(modules.items(), key=lambda item: (-item[1][1], item[0]))[:limit]:
        share = 100 * seconds / total if total else 0
        lines.append(f'| {label(name)} | {count} | {seconds:.3f} | {share:.1f}% |')
    lines += ['', '## Slowest individual cases', '', '| Test | Outcome | Seconds |', '|---|---|---:|']
    for case in sorted(cases, key=lambda c: (-c.seconds, c.module, c.name, c.outcome))[:limit]:
        lines.append(f'| {label(case.module)}::{label(case.name)} | {case.outcome} | {case.seconds:.3f} |')
    return '\n'.join(lines) + '\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('junit', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--limit', type=int, default=25)
    args = parser.parse_args()
    try:
        markdown = report(read_cases(args.junit), args.limit)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(markdown, encoding='utf-8')
        summary = os.environ.get('GITHUB_STEP_SUMMARY')
        if summary:
            with Path(summary).open('a', encoding='utf-8') as stream:
                stream.write(markdown)
    except (OSError, ValueError, ET.ParseError) as exc:
        parser.exit(1, f'Timing report error: {exc}\n')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
