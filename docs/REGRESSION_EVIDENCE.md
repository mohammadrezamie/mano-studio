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

## Four-worker regression pilot — 2026-11-26
Opt-in tooling `docs/tools/shard_plan.py` balances historical testcase times with deterministic longest-first scheduling. It checks full exact pytest collection against the plan, rejects missing/duplicate IDs, and selects only a named shard; not activated in release CI. Local 7 tests passed (0.48s), including actual synthetic pytest run and matching JUnit identities; exact blobs dc8b39256a0873954b33c94790979d64f05d61df and 58f006d3082bff47cd0a1955f1679e6a15404ce7. Real fallback JUnit inputs (both 1,376 identities) independently planned and validated: Windows shard counts 286/287/287/516 and historical estimated times 2737.781/2737.781/2737.781/2737.780 s; Ubuntu counts 554/554/134/134, 581.164 s each. Ideal test-only critical path ~45m38s Windows, ~9m41s Ubuntu, vs ~3h02m31s/~38m45s cumulative, excluding setup, queueing, fixture changes, order and runner overhead. Not measured runtime improvement. Plan is revision-specific; verify all shard reports and coverage union against complete serial suite before any workflow replacement. No active Stable CI altered.

Usage from repo root: `python docs/tools/shard_plan.py plan regression.zip shards.json --workers 4`; run each index 0–3 in a separate worker on matching collection via `python docs/tools/shard_plan.py run shards.json 0 --junitxml=shard-0.xml`. Do not use fallback timings as acceptance for a different test collection.

Beta source-edit safeguard on efc631fd61a4ddc298d734eda9a01b063cb7dfa5: explicit bilingual Edit source action protects live CPU before source detachment; Save/Discard/Cancel, read-only while associated CPU active, unassembled draft unlocked, programmatic edits restore source. Two new locale GUI cases authored, Qt not available locally. Current Stable exact Ubuntu 1416 passed, Windows pending and #26 installer queued as last observed. No public release.

## Shard result audit — 2026-11-26
Added offline `docs/tools/shard_audit.py` to check the complete ordered set of shard JUnit ZIPs against the exact serial baseline and planned per-shard identities. Rejects missing reports, duplicate identities, misplaced tests, failed/error/skipped cases and coverage mismatch. Reports hashes and counts; same_revision_verified and public_release_approved remain false: verify source SHA/CI provenance separately. Actual local combined pytest: 15 passed in 0.64s (8 new audit tests and 7 existing plan tests), one pytest-asyncio environment deprecation warning. Verified blobs 9fa3d8bd4761676afbc2ea84b7142fbd7a9d1f1d and d261982c63a9a4f5d1866d6c11e5d8d1e0a7370e. Synthetic fixtures, not a four-worker Windows run. Usage: `python docs/tools/shard_audit.py shards.json regression.zip shard-0.zip shard-1.zip shard-2.zip shard-3.zip --output audit.json`. Each ZIP contains only regression.xml. Existing active release CI untouched; pilot not yet production gate.

## v1.0.0 full cross-platform regression — 2026-11-26
Original #24 exact source 3ed419e3a37d9e233a4a908c08f9eccbbe80bf83: run 45798904930 both jobs SUCCESS. Actual Windows job 139836644580: 1,416 passed in 8242.08s; Ubuntu job 139836644367: 1,416 passed in 3631.56s. Downloaded actual JUnit ZIPs 15119999661 (Windows) and 15109449408 (Ubuntu), both CRC valid; offline verifier confirmed exact same 1,416 unique identities, 0 failures/errors/skips on each platform. Machine-readable evidence docs/v1-regression-evidence.json records exact archive hashes and timing. Workspace share 99.69% Windows, 98.99% Ubuntu. This closes original #24 serial regression gate, not final redistributed candidate #26 (run 45809656420 queued at last inspection), native clean/pre-equipped PC acceptance, security or licensing gates. No public release. Beta 5d2309d48ef3ce4cf311c76f36b984d29abce427 supports reopening native assembly drafts; 10 local tests passed, Qt pending. #25/#27 reconciled with visual heads 54b713f001b6d766a962464907617898adde8456 and 3785db565e2eb709a6a9708b5d34d45b22adfe39; both mergeable.
