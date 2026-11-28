# Native release acceptance (not performed by hosted CI)

Both Stable and Beta require the same two native Windows x64 scenarios: clean machine with no separate Python/Qt/pip, and a pre-equipped machine. Use disposable VM snapshots and a standard user. Do not disable security software or bypass SmartScreen. Use only the exact owner-authorized internal review candidate in a disposable test environment; the current drafts are unsigned and are not approved public deliverables. Verify SHA-256 and the successful GitHub post-build attestation before testing. If Windows security blocks execution, record the block and stop; do not bypass it. Manual distribution and automatic installation have distinct trust requirements under the current main RELEASE_POLICY.md.

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

Historical Stable candidate e4bae9ed7b5112f1499d02bcfc20db66fb9085dd: 1561 tests per OS, both smoke PASS, 286 files and 111 binaries independently verified. Setup unsigned, 6 redistribution and 3 runtime review flags; native acceptance false. PySide6 6.12.0 still listed on PyPI; OpenSSL 3.5.10 announced for Dec 1 2026. Qt guidance requires corresponding source under distributor control, applicable notices and relinking rights. Upstream PySide source index https://download.qt.io/official_releases/QtForPython/pyside6/PySide6-6.12.0-src/ is a research lead only, not complete corresponding-source proof. Sources: https://pypi.org/project/PySide6/ ; https://www.openwall.com/lists/oss-security/2026/11/24/14 ; https://www.qt.io/faq/qt-open-source-licensing . No flag cleared.


## Current exact-candidate handoff — 2026-11-28

| Channel | Exact Setup SHA-256 | Source commit | Internal Actions review download |
| --- | --- | --- | --- |
| Stable 1.0.0 | `3525135132eaabe6039e3c543911ac6429e71e453b53792968e91fb1a142ef9c` | `926272ff0ebfa4731cfb0b00c149c7e12b4d5a56` | https://github.com/mohammadrezamie/mano-studio/actions/runs/46041711466/artifacts/15221272367 |
| Beta 1.1.0-beta.1 | `8fcd72cc280892de6c76c76d555ab4c6601b9e9753cb13157ca0c01ee127a0bc` | `2dd55994d36f2596dd3d17ea54dd3c3e43829ae2` | https://github.com/mohammadrezamie/mano-studio/actions/runs/46041711466/artifacts/15220751219 |

Both exact versions passed hosted install acceptance (46044104396 and 46043046471), reconciled regression (46102530937), and signed post-build verification (46050465305). Both private drafts now hold the exact binaries and retained evidence archives (46103521799). These are not Windows desktop native independent test results. The review artifacts may require GitHub login. Extract the outer archive and check the inner EXE, not the outer ZIP. For example, in PowerShell use `Get-FileHash -Algorithm SHA256 -LiteralPath .\ManoStudio-Setup-v1.0.0-x64.exe`. With GitHub CLI installed, the retrospective verification command is:

```powershell
gh attestation verify .\ManoStudio-Setup-v1.0.0-x64.exe --repo mohammadrezamie/mano-studio --predicate-type https://github.com/mohammadrezamie/mano-studio/attestations/reviewed-asset/v1 --signer-workflow mohammadrezamie/mano-studio/.github/workflows/attest-reviewed-assets.yml
```

Use the equivalent Beta filename for Beta. No independent Windows 10/11 VM or physical desktop is available to the current assistant. An authorized human with such an environment is needed to execute and record this handoff. Do not add more redundant CI gates as a substitute for these observations. Source correspondence and applicable security review remain separate. See official Qt obligations https://www.qt.io/development/open-source-lgpl-obligations .
