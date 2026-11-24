# Windows-first delivery plan

Owner decision, 2026-11-24: Windows 10/11 x64 is the sole delivery target for the next classroom week (2026-11-30 to 2026-12-06). This is a target, not a guaranteed date or authorization to publish a public release. Linux remains a regression environment; Linux distribution, Android, iOS and macOS packages are deferred. Do not introduce a web/mobile runtime or rewrite the desktop stack merely to claim cross-platform support.

## Architecture contract
- Academic `rtl_translator.py` stays one standalone readable Python file; no UI, platform or network imports.
- Domain engines (assembler, CPU, arithmetic, circuit documents, sequential logic) remain independent of Qt and OS-specific services.
- Qt desktop views consume actual engine state. Keep domain behavior out of paint routines and avoid parallel implementations.
- File/preferences, updates and Windows packaging are boundary services. Explicit consent for network activity. No login or telemetry.
- Keep dependencies minimal, inspectable and justified. Review module coupling, state invalidation, cancellation, exception boundaries and data loss paths. Prefer incremental refactoring with tests to a rushed rewrite.

## Acceptance checklist (not completed)
1. Primary RTL workflow: file/IDE/guided input, diagnostics, correct separate ASM export, standalone defense source; verify instructor dialect.
2. Windows-native usability: redesign visual hierarchy, typography, colors and purposeful motion; keyboard navigation, resizing, DPI scaling; both languages, all three themes, no clipped labels or missing glyphs.
3. Optional tools: CPU, debugger, arithmetic/base converter and circuit design must complete real representative tasks, not just display decorative controls.
4. Distribution: reproducible x64 frozen build, clean Windows install/launch/offline smoke, save/load, upgrade and uninstall; retain settings and user documents.
5. Updating: check and release metadata already implemented. Installation stays unavailable until authenticated installer verification and upgrade safety are tested.
6. Evidence: exact-head regression logs, artifact/hash, actual Windows screenshots and explicit manual owner acceptance. Do not confuse source smoke with an installed binary.

## Portability later
Keep the reusable domain engines and file formats; Linux package and native integration after Windows approval. Mobile requires a touch-oriented interface, lifecycle/storage adaptation, platform packaging and its own acceptance tests. No mobile implementation this week. Reassess Qt/mobile or another UI technology only after measuring actual requirements.
