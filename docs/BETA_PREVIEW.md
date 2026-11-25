# Small beta preview — acceptance definition

The user wants an early usable preview representing the whole book; this is not full curriculum completion or permission to publish. Current version remains 0.3.0-dev.1. The proposed next test milestone is a 0.x beta candidate, not a renumbering to 0.1 or a committed calendar deadline.

| Gate | Current state |
|---|---|
| Academic RTL translator, 25 named instructions, separate Python file | Implemented in documented dialect; instructor dialect verification open |
| Bilingual desktop/editor, export, settings, offline, three themes | Implemented; main regression passed, manual bilingual review remains |
| Learning Center and working Computer/Logic labs | 40 routes across all 13 indexed chapters; chapter 13 shared bus, crossbar and atomic lock experiment implemented |
| Brand, splash and visual feedback | Procedural implementation; current render tests/native review pending |
| All 13 chapters represented by at least one verified interactive exercise | All 40 routes represented; automated main CI passed, manual scientific/visual review remains |
| Exact-head Windows/Ubuntu regression | Verified main 9eb19971: 928 tests passed on each platform; follow-up branch pending |
| Real Windows x64 candidate artifact, smoke, installer if requested | Not verified; manual workflow dispatch unavailable through current connector at prior check |
| Visual owner acceptance and publication | Not done; separate explicit approval required |

No calendar estimate implies background work. Advance by testable milestones during active development sessions. Keep gaps explicit; no pretending that a chapter index equals scientific coverage. See RELEASE_POLICY.md and BUILD_CANDIDATE.md. No change to independent translator or update consent.

## Readiness estimate and freeze gates
Owner asked 2026-11-25 about remaining work. Qualitative estimate: 70–75% readiness for a small initial beta, 25–30% remaining, not measured completion or a calendar promise. All 13 chapters have implemented representative routes, but exact-head evidence is incomplete. Do not conflate additional features with beta readiness. Before a first candidate: (1) verify full exact-head Windows/Ubuntu CI and resolve failures; (2) audit every entry and core workflow in both locales, including missing translations and right-to-left layout, accessibility and scaling; (3) collect actual current screenshots and confirm no severe visual defects; (4) verify a Windows x64 candidate artifact and smoke only after owner authorization, with installer/manual approval as required. Instructor dialect confirmation remains open. Freeze beta feature scope once representative paths are verified; deeper curriculum is a separate backlog. No tag or publication without explicit approval.


## Beta quality checkpoint: actual visual route evidence and functional pin states
Owner reaffirmed international conventions, original high-quality visuals and scientific accuracy. Added numeric 0/1 state labels at functional gate terminals in both ANSI-style and IEC-style drawings; terminal and inversion-bubble roles are separately tagged for geometry regressions (not package pin numbers). Explicit RTL/LTR dialog direction in Learning Center, Computer and Logic labs; technical editors and schematics retain LTR. Added regression for all supported gate/arity/style combinations and both-locale route/document preservation. Expanded existing CI screenshot script to render each unique learning route in English and Persian dark theme, with Learning Center images and a JSON manifest mapping all 40 catalog entries per locale to actual images, dimensions and SHA-256. Existing three-theme editor/selected lab captures retained. Capture is automated offscreen evidence, not manual visual approval or formal IEC/IEEE certification; other themes for every route, native scaling and accessibility review remain open. Latest observed cache workflow 45485766455 green, counterpart pending; other latest CI pending. No installer dispatch, publication, new dependency or translator changes.


## Beta correctness and localization: real translation path
Corrected virtual-memory canvas: TLB hit uses a distinct bypass to physical address, resident TLB miss uses page table, page fault visits simulated backing storage with dirty writeback/load indication. Active routes are derived from completed model events, not an invented timing sequence; inactive paths dashed, labels distinguish bypass, fault and load. Localized CAM match/priority, paging counters/status, cache hit/miss and traffic, serial format and start/parity/stop/overrun errors and counters; technical hex controls explicitly LTR, crossbar wait/request labels localized. Added both-language transaction-feedback test for the three real paging cases, cache hit/miss and serial parity error. Existing scientific models unchanged. Prior CI still pending at inspection; latest cache run 45485766455 success, no latest exact-head pass or native visual acceptance claimed. No new dependencies, installer or translator changes.


## Post-merge visual review increment
PR #9 merged into main as 9eb19971b91af8f218988a0fb9ba294eb1155603 on 2026-11-25. Both pre-merge exact-head runs 45491944270 and 45491959562 succeeded. Post-merge main run 45511520586 succeeded on Windows and Ubuntu: 928 passed, one PytestRemovedIn10Warning each; actual desktop preview capture and upload succeeded, artifacts 14978228331 (Windows) and 14976968147 (Ubuntu). Source integration only; no installer/release or native visual acceptance.
New branch quality/beta-visual-review starts from verified main. Removed the iterator parametrize deprecation identified in logs. Added developer-only offline index.html to screenshot artifacts: all 13 chapters, side-by-side en/fa route captures, original-image links and other three-theme captures. Validate full entry/locale coverage, route identity, PNG header dimensions and SHA-256; fail capture if evidence is inconsistent. Tests authored for missing/duplicate/incorrect route, image, hash, dimensions and missing file. No screenshot pixel review or formal certification claimed; new CI pending. No runtime dependency, academic translator or packaging/release changes.
