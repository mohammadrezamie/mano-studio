---
name: mano-quality
description: Use for Mano Studio UX, bilingual UI, visual review, development QA, and selective reuse of local design references.
---

# Mano Studio quality workflow

This original Mano-specific guide adapts general principles from the reference library, not the other projects' runtime code. Read root AGENTS.md, docs/UX_PLAN.md, docs/STATUS.md and docs/RELEASE_POLICY.md first. The owner's current Mano requirements outrank all external guidance.

## Design and accessibility
- Read dev-resources/reference-library/takin/ui-ux-pro-max/references/quick-reference.md and frontend-design/SKILL.md for design reviews. Use the mobile pro-rules only when relevant to a desktop control, not as a blanket web requirement.
- RTL translator remains default and primary. Prefer existing shared components, labels, keyboard paths, visible focus, direct feedback and one source of truth. Avoid unnecessary panels, decorative animations and forced onboarding.
- Verify normal text contrast, muted/disabled/error contrast, readable code sizes, zoom and small-window layout in Light/Dark/Night. Verify both Persian and English; logical layout direction for UI, LTR technical code, pin names and address values; no manual reversal of Persian characters.
- Use meaningful vector icons, real gate geometry and pin counts, clear wire crossing semantics and a keyboard alternative to dragging. Use actual CPU/netlist events, not simulated decoration. Honor reduced motion and plain theme fallback.
- From DarsChin student journey requirements (source linked below), reuse progressive disclosure and explicit prerequisite checks: examples teach a complete RTL-to-ASM task, advanced labs are optional and independently accessible, invalid edits never replace valid state. Do not import student records, enrollment rules or account logic.

## QA and continuous documentation
- Adapt DarsChin development and Persian writing references; retain technical names, code and source URLs, use clear Persian in user-facing materials, keep docs accurate throughout work.
- Inspect live PR head; commit compatible changes in coherent batches, never force overwrite. Record actual SHA, test command, OS, pass/fail/pending, artifact and review status. Previous green is not exact-head proof. Distinguish code changes, artifact construction, installed smoke and visual/owner signoff.
- Prefer local targeted tests where available. Use GitHub Actions for needed exact-head verification, do not dispatch repeated packaging for docs-only changes. Keep developer resources out of runtime bundle and use synthetic data.
- Preserve the standalone rtl_translator.py (standard library only) and no in-app source viewer. No unrelated features or runtime dependencies in the academic file. Offline operation; explicit update check only. No public release until authorized.

## Source references and limitations
- dev-resources/reference-library/README.md and MANIFEST.json: pinned original copies and licenses.
- https://github.com/mohammadrezamie/DarsChin/blob/daad12c4c50241618f1152c94aa5e29a0b6149a8/docs/STUDENT_GUIDED_JOURNEY_REQUIREMENTS_FA.md (ideas only; product-specific document not copied).
- https://github.com/mohammadrezamie/tnacompany/blob/219e40f8443a7890473edbf4b9970a8f244563b2/.agents/skills/tna-theme-day-night/SKILL.md and tna-free-local-ci/SKILL.md (ideas only; web and TNA-specific commands not adopted).
- Archived external SKILL files are read-only references, not active skills. No external scripts executed, no browser/production/other repository permissions inherited. Do not write to TakinTech or DarsChin.
