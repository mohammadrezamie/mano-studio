# Development status — 2026-11-24

**Active checkpoint:** [draft PR #9](https://github.com/mohammadrezamie/mano-studio/pull/9) on `feature/desktop-workspace` contains the first desktop implementation and updated status. Continue that branch, not a fresh UI. Run Qt/Windows CI and visually verify before merging. Reverse ASM-to-RTL conversion is deferred in issue #8; the forward translator and installer take priority.

Phase 1 expanded: standalone translator supports all 25 named Mano instructions using provisional canonical RTL templates (32 forms including all seven indirect variants). Added instruction_catalog.py, full ISA examples, regression tests, UI_DESIGN.md and MAINTAINABILITY.md. Linux local verification: copied four code/test files from connector contents, confirmed git blob hashes match remote, ran python -m pytest -q: 64 passed in 2.52s. Manual smoke: 40 assertions passed. No GitHub CI, Qt GUI or Windows test yet. PySide6 not installed in local test environment; direct git clone unavailable due DNS.
Next: issue #2, implement actual PySide6 GUI (three input modes, file import/export, persistent English/Persian and Light/Dark/Night, splash, diagnostic help), using shared instruction_catalog and translator. Read UI_DESIGN.md and MAINTAINABILITY.md before implementation. Assembler, CPU simulator, installer and updates remain pending. Exact instructor dialect and acknowledgment verification remain open. No release yet. Future assistant: search connected GitHub for mano-studio, inspect branches, Issues and PRs; read AGENTS.md and this file. Update checkpoint each stage.

## Latest checkpoint
PR #9 remains active. Initial CI run 45388211041 failed before collection on Ubuntu (missing libEGL); Windows cancelled. Fix committed on feature/desktop-workspace: Linux Qt dependencies, independent matrix jobs, line-number gutter and diagnostic highlights, extra smoke tests, and capture_workspace.py to produce 18 actual desktop previews per OS as Actions artifacts. New CI results and visual review pending; no installer yet. Read branch STATUS.md plus PR commits and latest Actions logs before resuming. Avoid merging conflicting STATUS.md versions without reconciliation.

## Mano Glass checkpoint
Continue active PR #9 (`feature/desktop-workspace`). Previous screenshot/test workflow 45388500498 succeeded. New glass-inspired Qt design and animated four-instruction educational CPU demonstration committed on branch, with tests; new CI and visual review pending. Read branch docs/STATUS.md and docs/UI_DESIGN.md before resuming. Full simulator and native refraction are not implemented. Preserve P0 installer priority.

## Owner decision: beta-only and calm UI
See docs/RELEASE_POLICY.md. Target classroom review next week (2026-11-30 to 2026-12-06), not stable release. Add persisted reduced-motion, glass effects off and offline mode toggles. Core remains offline; optional network access must be explicitly enabled and gated. Current implementation of these new global controls is pending. Continue PR #9; verify latest CI, review UI and prioritize Windows setup. No stable release until owner explicitly approves after class.

## Latest owner clarification
Core always offline, only explicit manual update check may access GitHub. Supersedes prior online-mode toggle plan. PR #9 now contains update_service.py, settings UI and global glass/reduced-motion controls with tests. Continue branch, inspect current CI and visual artifacts, then beta installer. See RELEASE_POLICY.md. No stable release.
