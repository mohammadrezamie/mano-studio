# First beta — native acceptance runbook

Use this only after an exact candidate has both successful regression and installer workflows. A source preview, offscreen screenshot or fixture test is not native acceptance. Do not test with personal documents. No publication without approval.

## Evidence record
- Source commit:
- Candidate version:
- Windows edition/build and architecture:
- Display scaling and resolution:
- Installer filename and SHA-256:
- Portable archive filename and SHA-256:
- Test operator/date:
- Result: NOT RUN / PASS / FAIL
- Known limitations and issue links:

## Test matrix (mark each independently)
| ID | Procedure | Expected |
|---|---|---|
| W01 | Verify Setup SHA-256 against candidate manifest; inspect publisher signature/status. | Hash exact; signature status recorded, not inferred. |
| W02 | Install to a fresh per-user Windows 10/11 x64 profile with network unavailable. | Installation and start menu shortcut succeed; no login or network dependency. |
| W03 | Launch via installed shortcut; inspect splash and icon. | M-chip visible, real version shown, no missing glyphs or artificial wait. |
| W04 | Open supplied add.rtl; convert and export. | LDA 100, ADD 101, STA 102, HLT, each on its own line. |
| W05 | Use visual builder and symbol pad; compare equivalent RTL input. | Same assembly result; arrow and brackets accessible. |
| W06 | Enter invalid RTL, then correct it. | Localized actionable diagnostic; no stale valid export; corrected input succeeds. |
| W07 | Open/save/export in a directory containing Persian letters and spaces. | Correct UTF-8 text roundtrip, no document loss. |
| W08 | Switch Persian/English and restart. | Language persists; Persian layout RTL, code and register data LTR. |
| W09 | Review dark/light/night at 100% and 150% scaling; resize. | Critical controls and text readable, no severe clipping; keyboard focus visible. |
| W10 | Disable motion and glass, restart, then enable them. | Preferences persist; no stuck animation; functionality unchanged. |
| W11 | Run bundled CPU example and step/back; inspect recorded datapath. | HALT and expected memory result; reverse step restores state; no invented hardware timing. |
| W12 | Open half/full adder and change inputs; inspect truth table. | Correct 0/1 values, only actual changed nets highlighted; standard functional symbols. |
| W13 | Open About in each language. | Instructor acknowledgment, course, version and license readable; confirm exact attribution before publication. |
| W14 | Explicitly check updates while disconnected. | Localized failure; editor remains usable. No automatic update install. |
| W15 | Locate bundled rtl_translator.py and verify hash against checkout. | Exact standalone academic source, no UI dependency. |
| W16 | Uninstall; inspect application directory and exported document. | Executable removed; user document remains. |
| W17 | Extract portable ZIP into another fresh path; launch offline. | Same core workflow succeeds, no installation needed. |

## Acceptance rule
A critical translator, data-loss, startup, installation, unreadable language or security defect blocks public beta. Record reproduction, environment and evidence for every failure; rebuild and retest affected paths after a fix. Confirm instructor-specific syntax and name spelling separately. Distribution license obligations, corresponding source access and signing status are separate gates. This document is a procedure, not a completed test report.

