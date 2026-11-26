# Frozen Windows source-family review — 2026-11-26

Actual portable ZIP from run 45809656420, exact source 0fa786aa55266bdded0e30eacfcc70e24e279eaa, SHA256 3456b4a7d659689706800592a4d206403956c0af249062237a5801481fc50ba1. Internal evidence only. This report identifies source-family **candidates** by binary names/locations, not exact corresponding source, legal entitlement, or vulnerability exposure.

| Candidate family | Binary count | Next review |
|---|---:|---|
| Microsoft runtime | 53 | Exact runtime versions and redist rights |
| QtBase | 18 | Module/plugin notices, exact source and build options |
| QtDeclarative | 5 | Determine need, then source or conservative pruning |
| QtWebEngine source family (Qt PDF) | 2 | PDF component and embedded third-party notices, not evidence of WebEngine browser binary |
| QtSvg | 3 | Source and third-party notices |
| QtImageFormats | 5 | Included image codecs and notices |
| PySide / Shiboken | 8 | Wheel-source mapping, patches, bindings |
| Software OpenGL | 1 | Identify actual upstream and notices |
| CPython | 2 | Exact source version |
| CPython extensions | 10 | Verify embedded third-party libraries separately |
| OpenSSL | 4 | Two DLL pairs, patch/version evidence |
| libffi | 1 | Exact version and license |
| PyInstaller bootloader | 1 | Exact source and exception |
| Total | 113 | Zero unclassified names; source verification still open |

Reproduce on inner portable ZIP: `python docs/tools/module_sources.py ManoStudio-v1.0.0-Windows-x64.zip`. Local actual tests: 20 passed in 0.04s, exact blobs b032c8ee192edc2c3e6692dfb30b0367fd208b25 and 6bb98814649bc17bfa3963a20f58a9a9ead07ad3. Ran classifier on actual archive: 113 binary paths, zero unmapped, corresponding_source_verified false, public_release_approved false. Classification is a name heuristic; a known family does not identify all embedded dependencies or exact build provenance.

## Ordinary PE import observations

Ran objdump -p on all 113 actual PE files (no executions). Qt6Pdf.dll has one observed ordinary importer: plugins/imageformats/qpdf.dll. Qt6Qml.dll imported by Qt6QmlMeta, Qt6QmlModels, Qt6QmlWorkerScript and Qt6Quick. Qt6Quick.dll had no observed ordinary importer; Qt6OpenGL.dll imported by Qt6Quick. opengl32sw.dll no observed ordinary importer. Qt's libcrypto-3-x64.dll imported by libssl-3-x64.dll, no ordinary importer observed for libssl-3-x64.dll. These observations **do not** exclude dynamic loads, plugin discovery, delay imports, resource loading or platform-specific paths. Do not remove any of these on this evidence alone. PDF/QML/Quick group is a candidate for a separate, dependency-checked lean payload experiment, not the current build. Keep known working binaries and CI intact.

## Upstream review references

- https://www.qt.io/development/open-source-lgpl-obligations — corresponding source and ability to replace/relink libraries.
- https://www.qt.io/development/download-open-source — module and third-party obligations.
- https://pypi.org/project/PySide6/ — published wheel listing still 6.12.0 at inspection.
- https://www.python.org/doc/versions/ — Python 3.14.10 release dated 2026-10-25.
- Candidate source trees: https://github.com/qt/qtbase/tree/v6.12.0 , https://github.com/qt/qtdeclarative/tree/v6.12.0 , https://github.com/qt/qtwebengine/tree/v6.12.0 , https://github.com/qt/qtsvg/tree/v6.12.0 , https://github.com/qt/qtimageformats/tree/v6.12.0 , https://github.com/pyside/pyside-setup . These are investigation starting points, not verified matching source archives or a distributor source offer.

No patched replacement has been confirmed. No new distribution approval. Current #26 GPL/LGPL text rebuild remains queued at last inspection.
