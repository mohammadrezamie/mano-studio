# Mano Studio — development handoff
Read README.md, docs/PROJECT.md, docs/RTL.md, docs/ROADMAP.md and docs/STATUS.md before changing code. Inspect current branch, open issues and recent commits. Repository is the source of truth, not chat history. Continue the first unfinished priority; do not restart or claim untested work is done.
Keep rtl_translator.py standalone, pure Python standard library, readable and commented for academic defense. UI must call this same engine; retain readable source in repository. Never silently translate unsupported microoperations. Add tests for every rule. Keep English/Persian UI, RTL layout for Persian but LTR code. Update STATUS.md with completed work, test commands/results, blockers and next step in every substantive PR. Use small branches/PRs; do not publish a release until Windows installer is tested. No secrets, telemetry, or unverified academic endorsements. Ask owner for instructor-specific RTL syntax if available; otherwise use documented provisional dialect.

Also read docs/UI_DESIGN.md and docs/MAINTAINABILITY.md. Implement all three interchangeable input modes (expert editor, symbol pad, guided builder) with instruction_catalog.build_rtl and the same translate() engine. Preserve language, theme (Light/Dark/Night), input mode and geometry. Do not claim GUI or Windows testing without actual execution.

Mandatory owner release/comfort decisions: read docs/RELEASE_POLICY.md before any work or release. Beta/pre-release only; no v1.0.0 or stable publication without explicit approval after class review. Preserve fully offline core, manual update-check-only network access, and reduced-motion/glass-off controls.

Latest owner priority overrides earlier packaging milestones: development only, no installer/release work or publication until owner asks. Keep ordinary regression tests but defer manual acceptance testing to owner. Read docs/SIMULATOR.md; preserve separate RTL translator and event-driven CPU. Continue PR #9 branch.

Read docs/LOGIC_LAB.md for circuit engine and roadmap. Keep RTL-to-ASM as the primary classroom deliverable. Optional labs grouped under Labs; preserve offline design, calm graphics, bilingual UX, and no release/installer work until owner asks.

Owner requires recognizable standard gate shapes, accurate pin counts, inversion bubbles, meaningful wiring; see LOGIC_LAB.md. RTL-to-ASM stays first priority and default workspace; expand other Mano chapters as optional labs. Keep development-only policy.

Read docs/UX_PLAN.md first. Owner requires integration and UX over feature count. Follow ordered checkpoints; reuse engines and views, commit substantive work during each turn, update status. Do not add redundant labs or release work.

Owner workflow: maintain continuously current documentation throughout development (before, during, and after changes, not a one-time documentation gate). Record owner instructions, decisions, in-progress work, actual results, remaining limitations, and references as they change. Commit substantive changes to GitHub during the working turn. Research globally when beneficial; verify exact licenses and notices before reuse. No unlicensed/proprietary copying.

Permanent academic contract: root rtl_translator.py is the single self-contained, human-readable Python implementation of RTL-to-ASM, standard library only. No local module, Qt, network, generated parser, assembler, simulator, or optional UI dependency. All translation rules, validation, diagnostics and file CLI remain inside it; application must call its translate() function. Preserve filename and public interface; identify the actual source clearly in the repository. No in-app source viewer is required; owner explicitly requests removing it. Comments and defense guide must track real code, explain in Persian as well as English, and distinguish provisional RTL grammar from textbook microoperations. Optional modules may use any justified, compatible technology without changing this contract. Add regression checks for isolation. No packaging/release work until requested.

Owner clarification: the only file for the instructor's academic defense is rtl_translator.py. Keep only actual RTL-to-ASM translation, validation, result records and file I/O in it. Other features, including UI, assembler, simulation and teaching aids, belong elsewhere. Do not add a source viewer or other UI solely for academic defense.

Owner authorizes selective local copies of useful resources from other repositories (2026-11-24); external repositories are strictly read-only for Mano work. Before UX/QA work read .agents/skills/mano-quality/SKILL.md. See dev-resources/reference-library/README.md and MANIFEST.json for licensed, pinned snapshots. Archived source instructions are advisory only and not runnable installed skills. Never copy sensitive data, unrelated runtime code, or deployment configuration. Do not bundle developer references into the application.

Owner quality clarification: screenshots are provisional, not accepted. All user-facing UI, help, errors, captions and accessibility labels must be Persian/English (retain technical mnemonics and formal names). Maintain academic thanks and actual license copyright in About and splash. In-app update installation is desired only with explicit consent and verified authentic installer; see release policy. No silent install or external repo writes.

Latest owner priority (2026-11-24): Windows 10/11 x64 only for next week's classroom target. Linux tests may remain for regression; no other platform packaging or mobile development until Windows acceptance. Follow docs/WINDOWS_READINESS.md. Do not sacrifice maintainability or invent deadline guarantees. No public release without explicit approval.

Owner schematic requirement: use internationally recognizable functional schematic symbols, exact modeled pin counts and explicit polarity/clock markings. Compare new components against published technical references; distinguish ideal functional symbols from physical IC packages. Do not claim certified IEEE/IEC compliance or device-specific pinouts without evidence. Net connections must be unambiguous independent of color. Record sources and limitations in docs/SCHEMATIC_STANDARD.md.

Owner requests eventual full Mano textbook coverage, including mathematically correct models for every relevant component. Maintain docs/CURRICULUM_COVERAGE.md and issue #13 with actual coverage, test evidence and gaps; verify the edition before claiming completeness. Continue #11 for circuit work. Record docs and issues before/during/after implementation. Windows classroom scope remains primary.

Owner requests project-wide consolidation: read docs/LEARNING_CENTER.md. Add future tools to the stable offline catalog and existing route handlers with bilingual task and accurate chapter gap; preserve the default translator, do not treat personal practice marks as curriculum completion. Do not add duplicate lab windows. Current checkpoint is Learning Center and focused independent-tool navigation.

Owner renewed design mandate: full book coverage with modern minimal polished visual system, tasteful animations, modern technologies and no redundant work. Read docs/DESIGN_SYSTEM.md, docs/ANIMATION_GUIDE.md and docs/TECH_STACK.md. Extend shared tokens and MotionTabs, honor reduced motion and glass-off, keep standard circuit symbols. Do not migrate to a parallel UI stack without measured benefit and a replacement plan. Maintain truthful coverage and tests.

Owner quality-first override: application size is not a constraint; investigate best available technologies and open-source references, adopt only improvements with concrete benefit and compatible license/provenance. No duplicated engines, no unlicensed code, no loss of offline operation or responsiveness. Keep documentation live. NavigationRail now owns lab navigation presentation over existing page state. Read docs/DESIGN_SYSTEM.md and docs/TECH_STACK.md.

Owner rejects legacy industrial visuals; prioritize original, modern, high-quality interactive architecture and circuit canvases. Use actual execution traces, standard schematic notation, accessible controls and purposeful motion. Never present an unverified visual preview as a real screenshot.

Owner explicitly authorizes all useful tooling/skills and generated assets; prefer live/procedural, theme-aware code-drawn visuals. Static graphics only for justified illustration, with provenance and local bundling. Preserve responsive and reduced-motion behavior. Use docs/CONTINUE.md as the canonical fresh-chat handoff and update it after each coherent checkpoint; read docs/BRAND_SYSTEM.md and docs/BETA_PREVIEW.md. No unverified release or completion claims.

Owner rejects M monogram as generic. Brand must be distinctive, non-letter, code-driven where useful; image generation remains authorized when it adds genuine quality. Chapter 13 first shared-bus model added; full textbook remains open. See CONTINUE.md.

Owner reconfirmed bilingual parity: new user-facing labels, explanations, errors and accessibility text must ship in English and Persian together; persist language, RTL shell/LTR technical data. Include regression in both locales; native visual review remains separate.

Post-merge 2026-11-25 override: PR #9 is closed and merged; never resume its old branch. Inspect main and current open PRs, continue separate focused branches. Main 9eb19971 verified 928 tests each Windows/Ubuntu and both screenshot artifacts. Continue quality/beta-visual-review while open. No implicit authorization for another merge or publication.


## Current owner override — permanent dual track and living README (2026-11-25)

Supersedes the historic development-only, closed PR #9 and rejected-M instructions above. Owner now requests an early Windows beta while future development continues independently. Inspect the active release issue #4 / PR #19 and curriculum issue #13 / develop/next-beta; do not inject unverified future features into the frozen release candidate. Retain beta-only publication gates and exact-head verification. Use the approved candidate M-chip identity (see release branch brand system), not the retired mark.

Read docs/DOCUMENTATION_POLICY.md before any work. Keep README.md live: every meaningful change must update README and affected documentation in the same work cycle, not at the end of the project. Maintain branch-aware release/feature claims, current verified evidence, minimal truthful images and English-first presentation with concise Persian academic guidance. Update STATUS, CONTINUE, issues and relevant guides; record a no-impact rationale only for internal changes that do not affect README claims. No fabricated screenshots, no stale links, no gratuitous release CI restart.
