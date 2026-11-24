# Mano Studio — integrated UX development plan
Owner direction 2026-11-24. Supersedes additive feature lists. Quality and usability over feature count. No installer, release or manual acceptance testing until requested.

## Product map
- **Translate (default, P0):** one document and one RTL-to-ASM engine. Text, symbol pad, and guided reference/builder are alternate ways of editing it, not independent documents. Import, translate, export is the dominant path. Examples and source mapping belong here.
- **Computer:** one assembler, one CPU, one execution state. Combine the former Live Lab and Program Lab. Examples, live datapath, registers, memory, I/O and debugger are different views of the same state. Do not create a second simulator for lessons.
- **Digital Logic:** one netlist engine and one canvas. Gate library, adders, encoders, decoders, custom circuits, truth tables and future sequential waveform views belong here. No separate dialogs for each component.
- **Learn:** contextual teaching, searchable offline references and examples reuse the engines and tools above. Data representation and arithmetic utilities appear where used, rather than standalone windows unless justified.

## Ordered checkpoints
1. UX audit and ownership: register the plan; remove duplicated entry points and unify CPU demonstration with program execution. Keep primary translation unchanged. Acceptance: example and custom program use CPU/assembler; one Computer entry; animation is derived from events and optional.
2. Primary translation refinement: simplify toolbar, source/output mapping, examples and inline instruction guidance, consolidate builder and reference; keyboard-free input, no stale export. Acceptance: new learner can import or construct RTL, translate, save ASM without opening an unrelated lab.
3. Visual system: consistent spacing, typography, icons and state hierarchy; subtle glass materials, no constant motion; compact and comfortable layouts, RTL localization; actual screenshots and accessibility review when appropriate. Avoid unverified claims of native glass or finished visual quality.
4. Digital Logic consolidation: standard gate shapes, accurate ports, integrated presets/free-wiring canvas and table; sequential models with clock/waveform as views. No duplicate calculations or decorative features.
5. Chapter coverage: selectively integrate ALU, data representation, register transfers, instruction cycle, memory and I/O; later control/pipeline/architecture topics when meaningful. Each module must serve a concrete learning task.
6. Owner-led manual review and distribution only on explicit request. Keep normal automated regressions but do not prioritize release work.

## Engineering gate
Before adding a new feature, identify existing capability to reuse, user task, why existing UI is insufficient, and acceptance criteria. Prefer an existing view over a new window. One source of truth per domain; independent pure Python translator preserved. No duplicated menus or engines. Every substantive change committed to GitHub during the working turn; update issue and STATUS.md with actual work, known limitations and next checkpoint. Repository commits are the live record of changes performed, not a claim of unattended development between chats. Keep draft PR #9 as active development and do not publish releases.

## Research and continuously maintained documentation
Maintain documentation continuously before, during and after code changes. Record owner instructions and scope as they arrive, and update actual status as implementation evolves. Record research links, relevant design patterns, license and reuse decisions. Reuse open-source code only after checking exact license, notices and compatibility; ideas may inspire original implementations. Update status after each meaningful code checkpoint. Research is purposeful, not a mandate to add features. Current step 2: consolidate instruction builder/reference and source mapping, keep one RTL document.

### Step 2 progress
Shared builder/reference panel implemented, separate reference dialog removed. RTL and ASM cursor positions linked via original translation line mapping; invalid/stale results do not navigate. Tests authored, runtime/visual verification pending. Next: examples and consistent file workflow, then step 3 visual system. Sources and reuse decisions logged in REFERENCES.md.

## Non-negotiable academic boundary
The actual RTL-to-ASM algorithm remains entirely in root rtl_translator.py, standalone Python standard library, readable and teachable; the UI and optional tools may evolve independently but must never replace, duplicate or hide it. Keep bilingual explanations and the standalone CLI. A copy of only this file must run without the repository or third-party packages. Mark the root file in README and the defense guide; no in-app source viewer.

### Step 2 — examples and file workflow checkpoint
Four integrated offline examples, Save As, document name/dirty state, remembered input directory, suggested ASM output filename and stale-output reset implemented. Removed unnecessary source viewer per owner request. The fixed Qt event-name collision passed 180 automated tests on Windows and Ubuntu (run 45395541255). New example/file changes await latest CI and visual review. Next: step 3 visual system refinement; keep translator independent and marked in README.

### Step 3 progress
Implemented shared visual tokens/QPalette, original vector action icons, editor panels, theme-aware code syntax, output state/count and offline status. Verified preceding step 2 CI (183 passed each on Windows and Ubuntu, run 45395897557). New theme regression case added; current run not yet confirmed. Next: inspect actual screenshots and resolve regressions, then refine integrated Digital Logic UX (step 4). No installer/release activity.

### Step 4 progress
Step 3 previous revision verified 184 tests on Windows and Ubuntu (45396606423); visual signoff remains pending. Step 4 started with shared editable circuit documents, embedded pin editor, apply/cancel/undo and local JSON save/open. All custom/preset circuits use the same Circuit evaluation and standard gate symbols. No new lab window or dependencies. Next: graphical connection and placement interaction and sequential views; verify new CI first.

### Step 4 — graphical editing checkpoint
Previous pin-editor revision verified 192 tests on each platform (45397436379). Added canvas source/receiving pin selection, drag placement, undo, backward-compatible coordinate persistence, obstacle-aware routing and SVG/CSV export in the same Logic Lab; table editor remains advanced component creation surface. Screenshot coverage extended to Logic and Computer. Latest tests and visual signoff pending. Next: verify new CI and address graphical issues before adding sequential clock/waveform views.

### First development candidate
Sequential models and waveform view integrated within Logic Lab. First build candidate explicitly authorized for GitHub Actions artifact only; see BUILD_CANDIDATE.md. No stable/public release, preserve academic core. Exact-head CI and visual acceptance required before signoff.

### Step 5 — integrated chapter coverage checkpoint
Added data representation and shared word arithmetic, 16 ALU operations with ripple stages, debugger with bounded reverse step and breakpoint trace, canonical reverse import. Previous exact head verified 265 tests per OS (45402185504). Latest base switching/trace optimization and new candidate smoke pending. Remaining: actual screenshots review, deeper instruction cycle and memory organization, classroom RTL dialect confirmation. No new standalone lab for these features.

## Windows-first priority override
Follow WINDOWS_READINESS.md; prioritize usable primary flows, native Windows visual quality, complete bilingual audit, maintainable service boundaries and tested Windows installation. Defer mobile, Linux distribution and optional scope expansion that jeopardizes the classroom target. No public release without approval.


## Project-wide Learning Center and focused tool navigation
Owner requested a transformative change across the project. Added one offline bilingual curriculum catalog spanning all 13 chapters and 33 real-tool learning entries across chapters 1–12. Each entry has a concrete exercise, stable route and honest chapter gap; chapter 13 is planned, not falsely marked implemented. Learning Center replaces the crowded Labs menu, with Ctrl+K, chapter/keyword search, unpracticed filter, explicit personal practice marks saved in QSettings, and direct navigation into existing Computer/Logic/translator surfaces. Practice count is not chapter completion or automatic mastery. Existing engines reused; no duplicate simulation, external network or new dependency. Computer hides unrelated CPU editor/controls when independent tools are selected and pauses the CPU timer while preserving state. Existing CPU tabs and primary RTL workspace remain intact. Added route/catalog and GUI regression tests. Previous DMA/FIFO head 1bb6f07 passed both Actions runs 45452014765 and 45451994986; current exact-head CI pending. Native Windows visual acceptance and remaining curriculum gaps pending. No installer, release, or academic translator edits. Next: verify current CI, refine responsive layout and connect additional chapters through catalog routes.


## Design system and motion checkpoint
Owner reaffirmed full Morris Mano coverage, exceptional modern minimal appearance, restrained purposeful animation, clean integration, modern technology and continuous documentation. Kept established PySide6/Qt 6 Widgets and shared scientific engines; no parallel shell or new dependency. Added shared spacing/radius/type tokens, improved learning center hierarchy and focus/list/progress styles, and lightweight 160 ms tab-indicator motion across editor, Computer, Logic and nested inspectors. Global reduced-motion preference snaps active indicators immediately; hidden/resized tabs snap, no idle animation or text/circuit opacity. Authored contrast-token, plain fallback, motion policy and UI role tests. Exact prior Learning Center head adbe584 passed both runs 45470016045 and 45470000518. Latest CI and native visual verification pending. Qt Quick is a selective future option, not implemented or required; see DESIGN_SYSTEM and TECH_STACK. No translator, installer or release changes.


## Quality-first lab navigation checkpoint
Owner removed the application-size constraint: select the highest-quality technology and assets by demonstrated benefit, license/provenance, maintainability, scientific correctness, offline compatibility and actual UX, not arbitrary binary size. Do not interpret this as permission to degrade responsiveness or copy incompatible code. Reviewed Ripes, Logisim-evolution, QFluentWidgets and Qt model/view docs for design patterns; original implementation only, no third-party code/assets or dependency imported in this increment. Added shared NavigationRail to Computer and Logic labs: 13 top-level pages accessed through labeled high-DPI SVG navigation, live sync with existing pages and learning deep links, persistent per-lab compact fallback with original tabs, keyboard list navigation, theme and RTL support. No duplicate pages or engines. Added new icons, shared rail styles and regression cases. Previous motion checkpoint exact-head CI was still running at initial inspection; current CI and native visual review pending. No translator, installer or release changes. Next: real visual QA, richer simulation diagrams and remaining curriculum, including cache/virtual memory/multiprocessors.
