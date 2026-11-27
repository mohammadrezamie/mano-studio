# Qt QML/Quick runtime pruning

The Mano Studio interface is implemented with Qt Widgets. The release source review found no application imports or UI references to QtQml, QtQuick, QQuick or VectorImage in the main window, editor, labs, splash or icons. Exact original Stable and Beta portable archives were independently tested after removing the same five Qt QML/Quick DLLs; the offline application smoke test passed for both copies.

The new build-time pruner removes only the exact five-library group, rejects unexpected QML binaries and any retained PE import into the group, records each removed file's SHA-256, and writes qt-qml-prune-evidence.json. It does not claim dynamic-load absence or security approval. Full exact-source regression, frozen portable/installed smoke, native Windows acceptance and manual security review remain mandatory.

Qt advisory CVE-2026-123706 affects VectorImage in Qt Quick through Qt 6.12.0. The release candidate avoids shipping the unused Qt Quick runtime rather than relying on an unreleased PySide build. Qt 6.12.1 itself is published, but PySide6 6.12.1 is not listed in the official Qt for Python download index as of 2026-11-27; use only the published PySide6 6.12.0 wheel until a patched PySide build is officially available.

References:
- https://www.qt.io/blog/security-advisory-cve-2026-123706-qt
- https://download.qt.io/official_releases/qt/6.12/6.12.1/
- https://download.qt.io/official_releases/QtForPython/pyside6/
