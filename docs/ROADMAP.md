# Roadmap
One-week target, not guarantee. P0: correct translator + tests, GUI editor and visual builder, file import/export, bilingual interface, Windows installer. P1: assembler and instruction-level simulator, update check, docs and examples. P2: timing visualization, richer debugger, recovery, reports, direct verified update installation.
Day 1: confirm dialect, implement standalone translator and tests. Day 2: expand verified rules and CLI. Day 3: desktop shell/editors. Day 4: visual builder, file operations and localization. Day 5: assembler/simulator if P0 stable. Day 6: Windows CI, installer, update checks and clean-machine testing. Day 7: fix bugs, defense guide, release candidate. Only explicitly marked 0.x prereleases are permitted for the classroom target. Stable v1.0.0 requires later explicit owner approval; see RELEASE_POLICY.md.
Acceptance: sample RTL file -> correct ASM file; same output via builder; invalid input diagnosed; English/Persian UI; installer installs/uninstalls on clean Windows; readable Python source accessible; offline translation; update check handles network errors. Never label untested features complete.

## Future bidirectional translation (P2, issue #8)
After stable RTL-to-ASM delivery, add assembly-to-canonical-RTL translation. Preserve forward mode, use shared instruction catalog, explicitly handle directives/labels, and test direct and indirect round trips. Reverse translation cannot recover arbitrary original RTL or formatting. Not required for initial academic delivery.

Classroom target: week of 2026-11-30 to 2026-12-06. Prioritize a tested Windows RTL-to-ASM beta. See [release and comfort policy](RELEASE_POLICY.md). Defer advanced visual effects and complete simulator if needed.

## Current priority override
Development quality first. Installer/release and manual acceptance are deferred until owner explicitly requests them. Expand core assembler, instruction-level simulator, program lab, calm graphics and educational usability. Classroom review does not require a release. See RELEASE_POLICY.md.

## Logic Lab expansion
See LOGIC_LAB.md for chapters 1–4 and future topics. Maintain optional labs separate from the required RTL translator. Develop custom circuit design, sequential logic, waveforms, ALU, data representation and chapter-aligned learning in incremental modules.

## Full-book coverage
Track all 13 original third-edition chapter families in CURRICULUM_COVERAGE.md and issue #13. Build original mathematically verified functional models incrementally. The classroom Windows candidate does not require full-book completion; prioritize quality and correctness over number of modules.


## Owner-approved parallel release and development — 2026-11-25
The owner explicitly asks to publish the initial beta while continuing future development. First release: PR #19 stays isolated from new features; active exact-head Windows/Ubuntu tests and installer, artifact integrity, native acceptance and redistribution gates remain mandatory. Public prerelease is authorized in principle by the latest owner request, subject to those gates; never publish an untested installer or stable release. Current connection has no release/tag creation or asset-upload operation. Next-beta development: branch `develop/next-beta` from prepared candidate c2fe262b, no PR while CI is congested. Next Chapter 13 increment: ideal MSI cache coherence (four masters, direct-mapped single-word lines, dirty writeback and invalidation, deterministic serialized accesses). Implement a pure model and independent tests first, then integrate bilingual UI into the existing Computer workspace and Learning Center after verification. No changes to academic translator or current release branch. Reconcile with accepted beta before opening the next-feature PR.


## Parallel next-beta: Chapter 13 MSI coherence — 2026-11-25
Owner explicitly requests public first beta and ongoing development in parallel. Isolated develop/next-beta branch starts from prepared c2fe262b. Added cache_coherence.py: ideal serialized four-processor MSI snooping, 16 words of 16-bit RAM, 4 direct-mapped one-word lines/core, BusRd/BusRdX/BusUpgr, dirty eviction and intervention writebacks, invalidation, immutable before/after snapshots. 20 local pytest cases passed in 0.35s, including 10,000 seeded accesses verified against an independent sequential-memory oracle and per-address MSI invariants, plus explicit transition cases and atomic invalid input. Source/test blobs match local ce6e6cb75f2d6dd469bfb4ee480fbe0c88470d9e and 6453dc34a76980622d6b090471a9b2b5dfd53e9d. Model only; no MESI, true concurrency, memory consistency model, electrical timing or integration into CPU cache yet. Next: bilingual interactive coherence page within existing Computer inspector, Learning Center route, UI regressions and visual evidence. No new feature PR yet (CI backlog). Release #19 and academic translator unchanged. Public beta requested but actual Windows artifact and release operations remain unavailable; release gates apply.
