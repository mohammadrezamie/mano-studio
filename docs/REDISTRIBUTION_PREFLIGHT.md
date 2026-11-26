# Public redistribution preflight — 2026-11-26

Separate release-quality PR based on exact v1 candidate 3ed419e3a37d9e233a4a908c08f9eccbbe80bf83; #22 and #24 remain frozen. MIT applies to Mano Studio's original code, not automatically to its bundled dependencies. This is engineering evidence, not legal advice or a legal determination.

## Actual candidate findings

Independent audit of the nested `ManoStudio-v1.0.0-Windows-x64.zip` from Actions artifact 15106817148 verified all 112 executable/DLL/PYD paths, lengths and SHA-256 digests against inventory, package notices and Python license hashes. Eight distribution records. Eight preflight flags:

- Qt6VirtualKeyboard.dll and qtvirtualkeyboardplugin.dll are present. Qt lists Virtual Keyboard as a GPL-only module in its open-source distribution. The project has its own on-screen RTL pad; confirm no dependency before removal.
- PySide6, PySide6_Addons, PySide6_Essentials, PySide6_Pdf, PySide6_WebEngine and shiboken6 metadata reports LGPL/GPL options, but each collected notice list contains only LicenseRef-Qt-Commercial.txt. The installed wheel metadata does not prove a commercial entitlement. No corresponding LGPL text was identified in those collected package notices; check other upstream notice locations. Do not misrepresent a commercial-only notice as complete LGPL evidence.
- Python and PyInstaller notices present; remaining Qt third-party, OpenSSL (two binary variants), Microsoft runtime, image codecs and other components still require attribution and redistribution mapping. Zero collector warnings does not mean approval.

## Remediation plan

1. Verify actual application imports, PyInstaller import graph, native dependencies and plugin runtime needs before changing packaging. Remove unused GPL-only Qt Virtual Keyboard plugin and library (and any unnecessary related modules) only in a new candidate; ensure existing custom RTL keypad still works. Verify no forbidden leftovers by scanning actual output, not just --exclude-module arguments.
2. Determine the correct official Community Edition wheel versions and provenance, pin exact tested build dependencies and hashes; obtain exact corresponding Qt/PySide/Shiboken sources and notices from official upstream. Include applicable license texts, third-party notices and source-access/replacement instructions. Do not invent license grants or use another edition's notice as evidence for these binaries.
3. Map every remaining binary to version, origin and applicable terms. Review dynamic-library replaceability, required corresponding source, installer behavior, and notices; obtain competent review. If GPL or commercial licensing is chosen, explicitly establish compatibility/authorization before publication.
4. Build a separate exact new candidate; run all regression, offline portable/installed smoke, native bilingual review and artifact verification. Do not promote either current candidate on the strength of a manifest hash alone.
5. Run `python -m installer.redistribution_gate path/to/portable.zip` on the actual nested portable archive. Exit 2 denotes heuristic flags; exit 0 means no implemented flags, not approval. Invalid evidence raises. This audit does not certify complete license text, source availability, provenance, signing, security or legal compliance. Manual review is always required.

## Verification

Local pure pytest: 8 passed (0.06s). Exact uploaded Git blobs: installer/redistribution_gate.py 699e42c1135f065e4cd9368f7c9d77fc65c470c4; tests/test_redistribution_gate.py d100de459c51c7a22e97276053e4a7974d0bc985. Actual archived v1: 112 binary paths, eight distributions, eight flags. No candidate rebuild, modification to academic core or publication in this checkpoint.

Official references checked 2026-11-26:
- https://doc.qt.io/qt-6.12/licensing.html (GPL-only modules)
- https://doc.qt.io/qtforpython-6/commercial/index.html (Community and Commercial distributions)
- https://www.qt.io/development/open-source-lgpl-obligations (distribution obligations)
- https://www.qt.io/faq/qt-open-source-licensing (source access and relinking)
