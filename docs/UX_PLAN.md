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

## Research and documentation-first workflow
For each new owner instruction, commit its interpretation and planned scope to documentation before code edits. Record research links, relevant design patterns, license and reuse decisions. Reuse open-source code only after checking exact license, notices and compatibility; ideas may inspire original implementations. Update status after each meaningful code checkpoint. Research is purposeful, not a mandate to add features. Current step 2: consolidate instruction builder/reference and source mapping, keep one RTL document.

### Step 2 progress
Shared builder/reference panel implemented, separate reference dialog removed. RTL and ASM cursor positions linked via original translation line mapping; invalid/stale results do not navigate. Tests authored, runtime/visual verification pending. Next: examples and consistent file workflow, then step 3 visual system. Sources and reuse decisions logged in REFERENCES.md.
