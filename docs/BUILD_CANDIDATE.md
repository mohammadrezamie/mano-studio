# Mano Studio 0.3.0-dev.1 — first development build candidate

Requested by owner 2026-11-24. This is an internal development checkpoint in draft PR #9, not a GitHub Release or a stable version.

- Required academic file: [rtl_translator.py](../rtl_translator.py), unchanged, standalone, marked in README.
- Main desktop: RTL/ASM, visual builder, offline examples, file workflow and three themes.
- Computer: assembler, instruction-level CPU, real-state view and memory/register inspection.
- Digital Logic: combinational presets, custom netlist and pin-aware canvas, v2 file, SVG/CSV; clocked D/JK/T/SR, 4-bit register/counter and sampled waveform view.
- Candidate gate: Windows/Ubuntu regression and actual screenshots; Windows x64 frozen portable smoke (translator, example, CPU, diagram export, clocked component), archive with SHA and dependency manifest, installer smoke and uninstall if successful.
- GitHub Actions artifact only, no release/tag, no installer publication. Build and manual visual acceptance are not confirmed yet. Unsigned; license/redistribution review required before public distribution. Instructor dialect still provisional.

Build orchestration: restored the proven simple push/PR Tests workflow. Run 45402415040 (c4884a1c2d2198700da6f4c09573e5600a0075d4) verified 266 tests on both Windows and Ubuntu, with real screenshot archives. The dependent build-job attempt again had no visible workflow run; reverted that experiment rather than block regular CI. The Windows development installer workflow is manual-only and independently runs regressions, builds and smoke-tests portable and setup artifacts. Source application smoke is now a pytest subprocess regression using the same entry point as the frozen app. Manual workflow dispatch is not exposed by the connected tool; no verified executable artifact yet. See https://github.com/mohammadrezamie/mano-studio/actions/workflows/windows-installer.yml . No public release.
