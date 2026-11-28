# Stable maintenance track — live checkpoint 2026-11-28

Base: frozen Stable 1.0.0. This branch is the independent Stable 1.0.1 maintenance candidate; update_service.VERSION is now 1.0.1. Keep this track separate from the frozen 1.0.0 release and do not merge it into the older candidate before its own gates pass.

## Exact verification

- First full run 46110206204 completed with 1,649 passed and 3 failed. All three were stale test expectations left at the old version: one asserted VERSION == 1.0.0, one expected v1.0.1 as the next release, and one incorrectly rejected 1.0.1 in version_policy. No tests were removed.
- Corrected tests: current 1.0.1 must not update itself; v1.0.2 is the next eligible Stable patch; the version policy permits 1.0.x patch releases. Exact correction commits: dbae8bf53857dba51618436e2cae5ce22ef50e9f and f7fcf04bd13bcc2dda712a554ef5d0718ec8f766.
- Fresh full regression + Windows Portable/Setup workflow: run 46111029889, queued at the last check. It runs full Ubuntu/Windows tests, then builds and validates the same Windows Portable/Setup payload, offline smoke, installed payload and hashes.

## Release restrictions

This candidate is internal evidence only. The bundled OpenSSL runtime remains 3.5.9; 3.5.10 is scheduled for 1 December 2026 and must be verified from the official release before public promotion. Qt/PySide source/relink, notices, security review and native Windows acceptance remain separate gates. No public release or automatic install is approved by this branch.

## Stable maintenance scope

Port only the offline platform-aware font selection and its tests from the tested Beta candidate. Preserve Persian/English layout and startup locale without changing the academic core, RTL-to-ASM conversion behavior, frozen 1.0.0 bytes or dependency pins. The separate academic handoff remains root rtl_translator.py.

## Update Center backport

Maintain the explicit installer-download, bounded official URL, length/SHA-256 validation, cancellation and nonblocking progress. Preserve Stable channel semantics. Automatic notification and trusted installation remain separate work; trusted publisher identity is not provisioned, so automated execution remains disabled.

---
# Stable maintenance track

Base: frozen Stable 1.0.0 source 5d72fb32867b2e37396ebac433b3bc28795e6c1f. Planned next patch: 1.0.1, not assigned to packages yet. Port only the offline platform-aware font selection and its tests from the tested Beta candidate 4d64fd1da99ae6c407b221c562062a87ec623afd; validate Persian/English layout and startup locale without changing the academic core, conversion behavior, release candidate bytes or dependency pins. Existing source version remains 1.0.0 until a new candidate is deliberately versioned. No release approval or claim of test success. Full exact-head acceptance and packaging required before a new patch release.

Development track: #57/#59/#60/#61 continue on the forward Beta line. Public distribution of existing releases is independent of both update tracks.

## Update Center backport
Port the previously tested Beta explicit installer-download, bounded official URL, length/SHA-256 validation, cancellation and nonblocking progress to the independent Stable patch. Preserve Stable channel and frozen 1.0.0 release. Automatic notification and trusted installation remain separate work, not enabled. Dedicated tests copied and included in maintenance acceptance. No public release claim.
