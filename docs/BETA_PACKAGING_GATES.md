# Beta Windows packaging and release evidence gates

**Status:** draft internal engineering gate for Beta PR #37. This document is not legal advice, security clearance, or permission to publish.

## Scope and separation
- Parent integration: PR #36, branch `integration/first-beta`, source `2b19fe4f0fcbdccb5f8d136cf509f1aaa28ea77d`, version `1.1.0-dev.1`.
- Packaging child: PR #37, branch `release/beta-packaging-hardening`, targeting `integration/first-beta` only.
- Stable candidate remains independently tracked in PR #26. No Beta-to-Stable promotion is implied.
- The only academic deliverable remains the isolated root `rtl_translator.py`; the GUI imports and delegates to it. No in-app source viewer or duplicate conversion engine.

## Parent evidence (not child acceptance)
- Combined focused integration run [45905561920](https://github.com/mohammadrezamie/mano-studio/actions/runs/45905561920): 622 core, 60 Qt and 20 workspace checks passed.
- Visual run [45905561919](https://github.com/mohammadrezamie/mano-studio/actions/runs/45905561919): 36 unique images independently decoded and matched to manifest dimensions and hashes.
- These results belong to the parent PR #36 source, not the later packaging child head.

## New packaging controls
1. **Pinned Windows build:** Python 3.14.10, isolated virtual environment, exact constraints, binary-only PyPI wheels, pip download report, SHA-256 records and `pip check`. The wheel evidence explicitly says it does not independently verify authenticity or grant redistribution rights.
2. **Qt payload pruning:** `installer/prune_qt.py` removes only the unused Qt Virtual Keyboard library/plugin after inspecting normal and delay PE imports of retained binaries. If a retained binary imports either target, pruning fails. Frozen portable and installed smoke tests remain mandatory.
3. **Notice inventory:** preserve raw installed `METADATA` text and hash every collected notice and binary. An inventory is evidence, not proof that all corresponding sources/notices are complete.
4. **Windows archive paths:** reject case-fold aliases, parent/file collisions, ADS/reserved names, trailing dot/space, unsafe characters and special ZIP entries before payload audit.
5. **Redistribution preflight:** compare actual DLL/PYD/EXE entries with inventory, hash binaries and notices, and flag GPL-only Qt markers, missing LGPL text, package notices and collector warnings. Exit code 2 means review flags, not an invalid build; no output ever approves publication.
6. **Runtime evidence:** scan actual bundled OpenSSL DLLs and the build interpreter's SSL version against the 3.5.10 review baseline. Unknown, missing or below-baseline evidence is flagged.
7. **Manifest binding:** candidate manifest requires matching Portable and Setup review reports, exact constraints copies, checksums, installed payload comparison, source hash and smoke evidence. It keeps `public_release=false` and `native_acceptance=false`.

## Exact-head gates
- Full regression on Windows and Ubuntu from `.github/workflows/tests.yml`; Windows uses the pinned Python 3.14.10 candidate environment and records wheel evidence.
- Windows package workflow builds Portable, runs frozen smoke, audits the actual ZIP, records runtime/redistribution evidence, builds Setup, installs it, compares the installed payload, runs smoke, uninstalls, and validates checksums and manifest.
- All artifacts must identify the exact source SHA. Older artifacts cannot approve a changed source.
- Independently inspect the actual uploaded ZIP/EXE and all reports; CI success alone is not a release decision.

## Known unresolved release risks
- Stable's prior inspected candidate contained OpenSSL 3.5.9, below the current 3.5.10 review baseline. The Beta workflow must measure its actual runtime and report flags; do not assume the same result or replace DLLs manually.
- Current reproducibility pins use PySide6 6.12.0. Aligned official patched Python/Qt/OpenSSL packages must be evaluated and rebuilt before final distribution.
- Qt LGPL/GPL corresponding-source, notice completeness, module licensing and dynamic/runtime dependencies require competent review. A commercial-only notice is not evidence of an LGPL grant.
- Clean Windows machine, normal-user install, offline first launch, upgrade/uninstall, native Persian/English scaling and keyboard behavior, signing and owner authorization remain separate acceptance gates.

**Decision rule:** this PR may produce an internal Beta development candidate only. No green test, manifest, wheel hash or smoke report independently authorizes a public Beta or Stable release.
