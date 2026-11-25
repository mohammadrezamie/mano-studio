# CI timing investigation

## Baseline (2026-11-25)

Exact #15 run 45557009008 passed all 1200 tests on both operating systems. Pytest reported Ubuntu 2466.13 s (41:06) and Windows 8981.63 s (2:29:41). These are test-suite durations, not application performance benchmarks. No per-test timing evidence was collected, so the reason for the difference is unproven. Do not remove tests or infer that Windows runtime is slow from these totals.

## Instrumentation

The proposed workflow retains the entire test matrix, font preflight and screenshot capture. Pytest prints its 30 slowest phases and writes JUnit XML. A standard-library developer script summarizes the top 25 modules and individual cases, counts outcomes, and appends a Markdown table to the Actions job summary. A separate per-OS timing artifact retains both XML and Markdown, including failed suites when a report exists. Screenshots retain their existing artifact name and contract. No new runtime dependency, parallel execution, cache or release change.

Reproduce locally with the same Python/Qt dependencies:
```sh
python -m pytest -q --durations=30 --durations-min=0 --junitxml=ci-reports/junit.xml
python dev_tools/ci_timing.py ci-reports/junit.xml --output ci-reports/timings.md
```

Local reporter tests: 7 passed in 1.40 s, Python 3.13.5. Test fixture covers passed/failed/error/skipped, timing order, ties, limits, escaping, invalid durations and CLI/step summary. Reporter is intended only for trusted local pytest output, not arbitrary uploaded XML.

## Next decision

Collect comparable Windows/Ubuntu results at the exact follow-up head before optimizing. Inspect slow setup/teardown and case durations; if one test dominates, profile it in isolation and preserve the same assertions. If independent cases dominate, consider balanced sharding only after verifying collection coverage and resource cost. Compare repeated measured runs and record wall time, total runner minutes and coverage. No speedup claimed yet. PR #16 remains untouched while CI runs. Integrate this branch after the current visual/academic checkpoint, not as a competing full test run.
