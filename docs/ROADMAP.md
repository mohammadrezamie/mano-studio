# Roadmap
One-week target, not guarantee. P0: correct translator + tests, GUI editor and visual builder, file import/export, bilingual interface, Windows installer. P1: assembler and instruction-level simulator, update check, docs and examples. P2: timing visualization, richer debugger, recovery, reports, direct verified update installation.
Day 1: confirm dialect, implement standalone translator and tests. Day 2: expand verified rules and CLI. Day 3: desktop shell/editors. Day 4: visual builder, file operations and localization. Day 5: assembler/simulator if P0 stable. Day 6: Windows CI, installer, update checks and clean-machine testing. Day 7: fix bugs, defense guide, release candidate. Only explicitly marked 0.x prereleases are permitted for the classroom target. Stable v1.0.0 requires later explicit owner approval; see RELEASE_POLICY.md.
Acceptance: sample RTL file -> correct ASM file; same output via builder; invalid input diagnosed; English/Persian UI; installer installs/uninstalls on clean Windows; readable Python source accessible; offline translation; update check handles network errors. Never label untested features complete.

## Future bidirectional translation (P2, issue #8)
After stable RTL-to-ASM delivery, add assembly-to-canonical-RTL translation. Preserve forward mode, use shared instruction catalog, explicitly handle directives/labels, and test direct and indirect round trips. Reverse translation cannot recover arbitrary original RTL or formatting. Not required for initial academic delivery.

Classroom target: week of 2026-11-30 to 2026-12-06. Prioritize a tested Windows RTL-to-ASM beta. See [release and comfort policy](RELEASE_POLICY.md). Defer advanced visual effects and complete simulator if needed.

## Current priority override
Development quality first. Installer/release and manual acceptance are deferred until owner explicitly requests them. Expand core assembler, instruction-level simulator, program lab, calm graphics and educational usability. Classroom review does not require a release. See RELEASE_POLICY.md.
