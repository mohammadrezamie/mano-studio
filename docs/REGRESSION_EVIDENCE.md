# Regression evidence — verified fallback and future CI acceleration

2026-11-26. Fallback #22, exact head ecb6647c38a93a4eb9c2171c99c10392abd15e72, [run 45786384171](https://github.com/mohammadrezamie/mano-studio/actions/runs/45786384171). Both jobs succeeded. Downloaded the actual [Windows JUnit ZIP](https://github.com/mohammadrezamie/mano-studio/actions/runs/45786384171/artifacts/15116515353) and [Ubuntu JUnit ZIP](https://github.com/mohammadrezamie/mano-studio/actions/runs/45786384171/artifacts/15107672117), verified CRCs and parsed 1,376 unique testcase identities per platform, exactly equal sets, no failure/error/skip. ZIP SHA-256 and per-module durations are in [fallback-regression-evidence.json](fallback-regression-evidence.json). This is fallback evidence, not a result for the newer #24 or #26 source and not publication clearance. Native/security/redistribution gates still apply.

## Reproduce

`python docs/tools/regression_evidence.py windows-regression.zip ubuntu-regression.zip --output report.json`

`python -m pytest -q docs/tools/test_regression_evidence.py`

Standard-library verifier, pytest for development tests only. Accepts the single regression.xml member from these trusted CI archives without extraction, bounds archive/XML size, rejects missing/duplicate test identities and mismatched counts, and exits 2 for unequal or non-clean reports. It does not authenticate GitHub provenance; confirm exact run and commit separately. Actual local result: 8 tests passed (0.05s) and verified both real archives. Exact tested tool and test blobs eed2cfd3042da1d42e7bf0f85ea692c7470f2d2c and e3abbc54c2a7b8703fa6bdc600d43ad64a60be46.

## Measured bottleneck

| Platform | Total testcase time | Workspace module | Share |
|---|---:|---:|---:|
| Windows | 10,951.123 s | 10,909.002 s | 99.62% |
| Ubuntu | 2,324.656 s | 2,300.322 s | 98.95% |

On Windows the longest single testcase is lab motion preference [fa] (533.97s); other expensive cases are shared motion, map geometry and state graph. These are elapsed test times, not proof of end-user performance or a specific root cause. Prioritize profiling construction and rendering of the full workspace/labs under Qt. Do not remove scientific or UI tests just to shorten a run. For future candidates, evaluate deterministic disjoint workspace shards across independent workers; verify the exact collected test set and every shard's result against a serial baseline before replacing full regression. Keep the currently running v1 and queued #26 jobs intact.

## Current development

Beta 6fcd55cae1c180bc141ef12ea0d59aadc8a5ad71 implements CPU close and reset guards; eight pure local guard tests passed, two locale GUI cases authored but not executed locally. Visual QA heads 0a6d639ba9c06296851b4ffc51cd1c2175e13d0a (#25), 4cae7be486ca1f10dca96db513873197c69ed308 (#27); both retain existing features and screenshot work. Source edits can still invalidate live CPU execution before close; follow-up remains open. No new issues or PRs. 
