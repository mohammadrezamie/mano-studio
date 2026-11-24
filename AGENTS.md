# Mano Studio — development handoff
Read README.md, docs/PROJECT.md, docs/RTL.md, docs/ROADMAP.md and docs/STATUS.md before changing code. Inspect current branch, open issues and recent commits. Repository is the source of truth, not chat history. Continue the first unfinished priority; do not restart or claim untested work is done.
Keep rtl_translator.py standalone, pure Python standard library, readable and commented for academic defense. UI must call this same engine; ship readable source alongside installer. Never silently translate unsupported microoperations. Add tests for every rule. Keep English/Persian UI, RTL layout for Persian but LTR code. Update STATUS.md with completed work, test commands/results, blockers and next step in every substantive PR. Use small branches/PRs; do not publish a release until Windows installer is tested. No secrets, telemetry, or unverified academic endorsements. Ask owner for instructor-specific RTL syntax if available; otherwise use documented provisional dialect.

Also read docs/UI_DESIGN.md and docs/MAINTAINABILITY.md. Implement all three interchangeable input modes (expert editor, symbol pad, guided builder) with instruction_catalog.build_rtl and the same translate() engine. Preserve language, theme (Light/Dark/Night), input mode and geometry. Do not claim GUI or Windows testing without actual execution.

Mandatory owner release/comfort decisions: read docs/RELEASE_POLICY.md before any work or release. Beta/pre-release only; no v1.0.0 or stable publication without explicit approval after class review. Preserve fully offline core, manual update-check-only network access, and reduced-motion/glass-off controls.

Latest owner priority overrides earlier packaging milestones: development only, no installer/release work or publication until owner asks. Keep ordinary regression tests but defer manual acceptance testing to owner. Read docs/SIMULATOR.md; preserve separate RTL translator and event-driven CPU. Continue PR #9 branch.

Read docs/LOGIC_LAB.md for circuit engine and roadmap. Keep RTL-to-ASM as the primary classroom deliverable. Optional labs grouped under Labs; preserve offline design, calm graphics, bilingual UX, and no release/installer work until owner asks.

Owner requires recognizable standard gate shapes, accurate pin counts, inversion bubbles, meaningful wiring; see LOGIC_LAB.md. RTL-to-ASM stays first priority and default workspace; expand other Mano chapters as optional labs. Keep development-only policy.

Read docs/UX_PLAN.md first. Owner requires integration and UX over feature count. Follow ordered checkpoints; reuse engines and views, commit substantive work during each turn, update status. Do not add redundant labs or release work.

Owner workflow: BEFORE implementing each new request, record the request, scope, and plan in docs/STATUS.md (and UX_PLAN.md if policy changes). Then commit code incrementally, update final status and issue. Research globally when beneficial; cite sources and verify license/compatibility before reusing code or assets. Never copy unlicensed or proprietary implementation. Prefer established patterns and dependencies over reinvention, keep offline operation and RTL priority.
