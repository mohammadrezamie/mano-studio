# Mano Studio 0.3.0-dev.1 — first development build candidate

Requested by owner 2026-11-24. This is an internal development checkpoint in draft PR #9, not a GitHub Release or a stable version.

- Required academic file: [rtl_translator.py](../rtl_translator.py), unchanged, standalone, marked in README.
- Main desktop: RTL/ASM, visual builder, offline examples, file workflow and three themes.
- Computer: assembler, instruction-level CPU, real-state view and memory/register inspection.
- Digital Logic: combinational presets, custom netlist and pin-aware canvas, v2 file, SVG/CSV; clocked D/JK/T/SR, 4-bit register/counter and sampled waveform view.
- Candidate gate: Windows/Ubuntu regression and actual screenshots; Windows x64 frozen portable smoke (translator, example, CPU, diagram export, clocked component), archive with SHA and dependency manifest, installer smoke and uninstall if successful.
- GitHub Actions artifact only, no release/tag, no installer publication. Build and manual visual acceptance are not confirmed yet. Unsigned; license/redistribution review required before public distribution. Instructor dialect still provisional.

Build orchestration: the original simple Tests workflow was restored after the reusable job variant produced no observable runs. A deliberate `build: candidate` push or manual Tests dispatch with `build_candidate=true` now uses an ordinary dependent Windows build job after both OS matrix tests and source smoke succeed. The separate legacy Windows installer workflow remains manual-only as a fallback. No automatic packaging on ordinary commits. Run 45402185504 verified 265 tests on Windows and Ubuntu after integrating ALU, history, debugger and reverse import. Latest interaction refinements and build pipeline are not yet verified.
