# Small beta preview — acceptance definition

The user wants an early usable preview representing the whole book; this is not full curriculum completion or permission to publish. Current version remains 0.3.0-dev.1. The proposed next test milestone is a 0.x beta candidate, not a renumbering to 0.1 or a committed calendar deadline.

| Gate | Current state |
|---|---|
| Academic RTL translator, 25 named instructions, separate Python file | Implemented in documented dialect; instructor dialect verification open |
| Bilingual desktop/editor, export, settings, offline, three themes | Implemented, regressions; newest exact-head CI pending |
| Learning Center and working Computer/Logic labs | 40 routes across all 13 indexed chapters; chapter 13 shared bus, crossbar and atomic lock experiment implemented |
| Brand, splash and visual feedback | Procedural implementation; current render tests/native review pending |
| All 13 chapters represented by at least one verified interactive exercise | Implemented routes for 13 chapters; newest exact-head verification pending |
| Exact-head Windows/Ubuntu regression | Latest checks pending |
| Real Windows x64 candidate artifact, smoke, installer if requested | Not verified; manual workflow dispatch unavailable through current connector at prior check |
| Visual owner acceptance and publication | Not done; separate explicit approval required |

No calendar estimate implies background work. Advance by testable milestones during active development sessions. Keep gaps explicit; no pretending that a chapter index equals scientific coverage. See RELEASE_POLICY.md and BUILD_CANDIDATE.md. No change to independent translator or update consent.

## Readiness estimate and freeze gates
Owner asked 2026-11-25 about remaining work. Qualitative estimate: 70–75% readiness for a small initial beta, 25–30% remaining, not measured completion or a calendar promise. All 13 chapters have implemented representative routes, but exact-head evidence is incomplete. Do not conflate additional features with beta readiness. Before a first candidate: (1) verify full exact-head Windows/Ubuntu CI and resolve failures; (2) audit every entry and core workflow in both locales, including missing translations and right-to-left layout, accessibility and scaling; (3) collect actual current screenshots and confirm no severe visual defects; (4) verify a Windows x64 candidate artifact and smoke only after owner authorization, with installer/manual approval as required. Instructor dialect confirmation remains open. Freeze beta feature scope once representative paths are verified; deeper curriculum is a separate backlog. No tag or publication without explicit approval.


## Beta quality checkpoint: actual visual route evidence and functional pin states
Owner reaffirmed international conventions, original high-quality visuals and scientific accuracy. Added numeric 0/1 state labels at functional gate terminals in both ANSI-style and IEC-style drawings; terminal and inversion-bubble roles are separately tagged for geometry regressions (not package pin numbers). Explicit RTL/LTR dialog direction in Learning Center, Computer and Logic labs; technical editors and schematics retain LTR. Added regression for all supported gate/arity/style combinations and both-locale route/document preservation. Expanded existing CI screenshot script to render each unique learning route in English and Persian dark theme, with Learning Center images and a JSON manifest mapping all 40 catalog entries per locale to actual images, dimensions and SHA-256. Existing three-theme editor/selected lab captures retained. Capture is automated offscreen evidence, not manual visual approval or formal IEC/IEEE certification; other themes for every route, native scaling and accessibility review remain open. Latest observed cache workflow 45485766455 green, counterpart pending; other latest CI pending. No installer dispatch, publication, new dependency or translator changes.
