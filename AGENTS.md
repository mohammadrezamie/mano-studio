# Mano Studio — development handoff

## Current controlling owner policy — 2026-11-26

This instruction supersedes conflicting historical deadlines, version targets, beta-only timing restrictions, development-only restrictions and academic-defense expansion requirements.

- Maintain exactly two permanent tracks in parallel: Stable (#4) and Beta (#23). Publish each independently when its applicable acceptance gates are met; Beta publication is optional and must be explicitly marked prerelease. Do not make Stable wait for the entire textbook or Beta scope.
- No mandatory v1.0.0 or fixed release date. The existing internal v1.0.0 candidate and verified artifacts remain valid historical evidence; choose the public version appropriate to the accepted scope and release history. Never rename an unverified artifact to imply stability.
- Stable means a genuinely reliable, polished, integrated application: verified exact-revision correctness, UI usability in Persian and English, offline behavior, standalone Windows install/upgrade/uninstall, security, redistribution and artifact authenticity. Freeze or defer unverified features rather than lower acceptance standards.
- The academic deliverable is exactly the standalone root `rtl_translator.py`: one downloadable Python file, standard library only, no sibling imports, Qt, simulator or network. Keep the desktop app calling this same core. The owner will independently learn the line-by-line explanation and prepare the defense. Do not prioritize additional defense tutorials, separate academic applications or presentation workflows over product development. Existing useful docs/examples remain available.
- Primary effort: build, integrate, improve and test the actual desktop application, premium readable bilingual UX and practical labs. Keep documentation concise and evidence-backed, not a substitute for implementation. Preserve zero-manual-prerequisite Setup and offline-first operation.
- Do not claim a release until actual publication and verification; retain all existing acceptance and security gates. No new fixed deadline, public version tag or release is created by this policy update.

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

Historical preference superseded 2026-11-25: owner approved the rounded microchip with an M mark from the vivid concept; preserve that recognizable identity, code-driven where useful. Chapter 13 first shared-bus model added; full textbook remains open. See CONTINUE.md.

Owner reconfirmed bilingual parity: new user-facing labels, explanations, errors and accessibility text must ship in English and Persian together; persist language, RTL shell/LTR technical data. Include regression in both locales; native visual review remains separate.

Post-merge 2026-11-25 override: PR #9 is closed and merged; never resume its old branch. Inspect main and current open PRs, continue separate focused branches. Main 9eb19971 verified 928 tests each Windows/Ubuntu and both screenshot artifacts. Continue quality/beta-visual-review while open. No implicit authorization for another merge or publication.

Owner visual mandate (2026-11-25, latest): full discretion over implementation, tools and art choices in service of final quality. The approved logo is the friendly microchip bearing the letter M. Do not revert to the rejected non-letter aperture. Generate images only where they materially improve quality; request no text in illustrations, with the approved M logo glyph as the sole mark exception. Compose all Persian and English UI copy, captions, and typography separately using actual localized text, not pixels generated by an image model. Choose readable Persian typography with correct shaping, bidi, wrapping and proportionate sizes; avoid oversized Persian headings merely for decoration. Code-render functional schematics, data and animation; use approved offline raster artwork selectively. Preserve accuracy, accessibility, reduced motion, glass-off and independent Python core. Release still requires verified Windows build and existing release-policy gates.

Latest release priority (2026-11-25): use release/beta-integrated first beta candidate, not old PR #9 or feature branches. Internal Windows packaging now authorized; freeze optional scope. Verify exact-head tests, visuals and actual installer artifacts before any merge or publication. Read docs/RELEASE_POLICY.md, docs/BUILD_CANDIDATE.md and final CONTINUE.md checkpoint. Retain approved M-chip and standalone academic translator.


## Living README — owner mandate (2026-11-25)
Read docs/DOCUMENTATION_POLICY.md before work. Keep README current with every meaningful change in the same work cycle. This permanent rule applies to release and next-generation tracks; prefer English, the approved M-chip, limited authentic imagery and verified status. Do not reset the active release CI for a docs change. Keep separate branch-specific claims, tests and limitations. Update STATUS, CONTINUE and affected guides as well. This supersedes historic development-only and rejected-logo decisions wherever they conflict.


## Practical laboratory mandate — owner 2026-11-26
Read docs/PRACTICAL_LAB_POLICY.md. Full textbook coverage requires useful interactive experimentation, real composable models wherever applicable, and curated saved ready-to-load samples in each relevant section with independent expected outcomes. Use shared simulation semantics, explicit port/clock/width contracts, validated save/load and undo; never claim unrelated models are integrated. Preserve offline bilingual operation and independent academic translator. Advance on next-beta; keep first Windows beta frozen except verified release blockers.

## Native document and updates — owner 2026-11-26
Use .mano as the native versioned application document envelope; retain legacy and academic exports. Expand validated persistence to all applicable lab types; never encode executable content or claim exclusivity/encryption. Optional Windows per-user association, user retains default-app choice. Explicit official GitHub update check/download only, validate digest and exact version/platform; no auto execution without trusted signing and verified upgrade. See docs/NATIVE_FILES_AND_UPDATES.md. First beta remains frozen.

## Permanent owner backlog — 2026-11-26
Read docs/OWNER_BACKLOG.md and issue #23 each continuation. Maintain all incomplete owner requirements, evidence and acceptance gaps there; never silently drop scope. Keep first beta release track independent, preserve academic translator and legacy exports.

## Owner deadline override — 2026-11-26
First stable instructor target is Monday 2026-11-30 (v1.0.0), conditional on actual evidence. This supersedes the earlier no-stable-before-class timing rule, not quality gates. Read docs/V1_DELIVERY_PLAN.md and issue #4 before continuation. Keep next-generation work independent and do not relabel beta binaries. Stable packaging guards must be deliberately revised on a separate candidate after beta validation.


## Owner visual-first delivery direction — 2026-11-26
The instructor's mandatory assignment is RTL-to-Assembly. Preserve one readable standalone standard-library Python file rtl_translator.py; no changes to its isolation or language. Prioritize excellent visual presentation and actual stability from v1.0.0 onward; optional new functionality can be promoted until the deadline only after independent verification and exact integrated acceptance. Retain distinct release and next-generation tracks. The owner permits suitable technologies, libraries and visual assets and no arbitrary package-size limit, subject to offline behavior, licensing and quality. See docs/V1_INSTRUCTOR_ACCEPTANCE.md and #4/#24. Do not merge unverified features merely to increase scope.
