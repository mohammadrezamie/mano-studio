# Native release acceptance (not performed by hosted CI)

Both Stable and Beta require the same two native Windows x64 scenarios: clean machine with no separate Python/Qt/pip, and a pre-equipped machine. Use disposable VM snapshots and a standard user. Do not disable security software or bypass SmartScreen. Wait for approved signed release candidates; internal unsigned packages are not public deliverables. Verify actual Setup SHA-256 against candidate manifest before running.

Copy the blank template `installer/native-observations.template.json` for each exact candidate. Record Windows build, actual architecture, standard user, reset snapshot, presence/absence of existing Python/Qt and offline conditions. Check both clean and pre-equipped machines, take actual screenshots/logs and record their SHA-256 hashes. Do not record PASS for anything not observed.

| Check | Actual action |
| --- | --- |
| offline-install / no-manual-prerequisites | Disconnect networking before installing, use normal Setup, no separate prerequisite installs or global changes. |
| private-runtime / no-global-path-change | Record resolved runtime locations and before/after user/system PATH; preserve existing Python, Qt and shared components. |
| offline-first-launch | Launch from Start menu without networking; verify complete splash and workspace; no automatic update traffic. |
| rtl-asm-roundtrip | Enter AC ← M[100] then S ← 0; expected LDA 100 and HLT. Export Assembly, reopen, validate reverse where supported. |
| persian-english-persistence / three-themes | Switch both languages and all themes, restart, verify persistence and legible labels. |
| glass-and-low-motion / keyboard-navigation | Toggle glass and reduced motion; keyboard-only editor, pad, builder, settings and dialogs. |
| display-100-150-200 | Test native display scaling at 100%, 150%, 200% with normal monitor/resolution; document clipping or focus failures. |
| save-open-reopen | Save and reopen text and applicable native exercises; ensure unsaved changes prompts work. |
| reinstall-preserves-settings | Normal reinstall of exact approved candidate with saved file/settings; verify user data stays intact. |
| uninstall-preserves-other-apps | Uninstall only Mano Studio; confirm unrelated runtimes, data and apps survive. |

Run from source checkout with Python 3.12+: `python -m installer.native_acceptance candidate-manifest.json ManoStudio-Setup-v1.0.0-x64.exe observations.json`. It checks exact Setup bytes, candidate identity, matrix completeness, recorded results and evidence-hash syntax only. Human reviewer must independently verify actual logs/screenshots and machine state; never infer authenticity, native PASS, signing, security or legal approval from structure. Template is deliberately NOT_RUN. No real native acceptance performed here. Keep evidence private when it includes machine details; redact before public posting.

Latest Stable candidate e4bae9ed7b5112f1499d02bcfc20db66fb9085dd: 1561 tests per OS, both smoke PASS, 286 files and 111 binaries independently verified. Setup unsigned, 6 redistribution and 3 runtime review flags; native acceptance false. PySide6 6.12.0 still listed on PyPI; OpenSSL 3.5.10 announced for Dec 1 2026. Qt guidance requires corresponding source under distributor control, applicable notices and relinking rights. Upstream PySide source index https://download.qt.io/official_releases/QtForPython/pyside6/PySide6-6.12.0-src/ is a research lead only, not complete corresponding-source proof. Sources: https://pypi.org/project/PySide6/ ; https://www.openwall.com/lists/oss-security/2026/11/24/14 ; https://www.qt.io/faq/qt-open-source-licensing . No flag cleared.
