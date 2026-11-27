# Exact binary review handoff — 2026-11-27

Current Stable candidate e4bae9ed7b5112f1499d02bcfc20db66fb9085dd (portable artifact 15179201788); prior candidate d3eeefec2536cca8b7fd4573bb436a4ab782075a (15177973782). Both outer and nested ZIP CRCs independently checked, all 111 binary paths, sizes and SHA256 verified, exact namespace membership. Between the two, no added or removed binaries; only ManoStudio.exe changed. This does NOT certify security or source compliance.

| Review lead (filename classification only) | Count |
| --- | ---: |
| Microsoft runtime | 53 |
| Qt base / plugin review | 18 |
| CPython | 12 |
| PySide / Shiboken | 8 |
| Qt Declarative | 5 |
| Qt Image Formats | 5 |
| OpenSSL | 4 |
| Qt SVG | 3 |
| libffi | 1 |
| Qt software OpenGL review | 1 |
| Application/PyInstaller | 1 |

Both candidates contain 11 Qt6 DLLs (Core, Gui, Network, OpenGL, Qml, QmlMeta, QmlModels, QmlWorkerScript, Quick, Svg, Widgets). No Qt PDF/WebEngine DLL in this Stable payload; package metadata is not proof of runtime inclusion. Qt6 and plugin group names are leads, not exact upstream component assignments; unknown DLLs and embedded third-party code require explicit review. Microsoft runtime provenance/redistribution terms, CPython bundled dependencies, PyInstaller exception, libffi, software OpenGL and Qt's statically included codecs remain open. Qt supplemental LGPL/GPL texts present; six package-specific review flags remain. Two distinct crypto DLLs report 3.5.9 and build interpreter SSL 3.5.0; three runtime flags remain.

## Next patched-build procedure

1. Verify official patched Windows wheels, pins and hashes; use compatible complete runtime, not manual DLL swapping. As checked today PySide6 public version is 6.12.0; OpenSSL 3.5.10 announced for 2026-12-01.
2. Rebuild exact candidate, run full independent test and install/portable evidence gates. Run `python -m installer.binary_review_map new-portable.zip --previous old-portable.zip`. Compare each added/removed/changed binary and package metadata/flags; no reuse of old review approval by filename.
3. Map actual Qt module/codec build configuration to matching Qt 6.12 source and upstream SPDX records; retain exact corresponding source, applicable notices and instructions for replacement under the distributor's control. PySide source archive index https://download.qt.io/official_releases/QtForPython/pyside6/PySide6-6.12.0-src/ lists 6.12.0 ZIP and tar.xz; actual source matching and retention are not completed. Official Qt third-party listing https://doc.qt.io/qt-6/licenses-used-in-qt.html documents source/SBOM leads, not proof of compiled components. See https://www.qt.io/development/open-source-lgpl-obligations and https://www.qt.io/faq/qt-open-source-licensing.
4. Complete actual native acceptance (#49), signing and owner/legal/security approval. No public release authorization from this tool or filename-based classification.

Source checks: https://pypi.org/project/PySide6/ ; https://www.openwall.com/lists/oss-security/2026/11/24/14 ; https://doc.qt.io/qt-6/licensing.html . Local independent comparison of both actual artifacts produced counts above. New reusable code and 15 synthetic test cases await focused CI; no product source or candidate version change.
