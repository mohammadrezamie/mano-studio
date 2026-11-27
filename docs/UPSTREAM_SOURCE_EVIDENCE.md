# Exact-candidate source acquisition (review only)

## Scope

Stable `5d72fb32867b2e37396ebac433b3bc28795e6c1f` and Beta `4d64fd1da99ae6c407b221c562062a87ec623afd` are frozen. Independent inspection of their actual portable archives (15180064025 and 15198955230) identifies the following native Qt libraries.

| Source family | Observed libraries | Channel |
| --- | --- | --- |
| qtbase 6.12.0 | Core, Gui, Network, OpenGL, Widgets | Both |
| qtdeclarative 6.12.0 | Qml, QmlMeta, QmlModels, QmlWorkerScript, Quick | Both |
| qtsvg 6.12.0 | Svg | Both |
| qtwebengine 6.12.0 / PDFium | Pdf, PDF plugin | Beta only |
| pyside-setup 6.12.0 | PySide6 and Shiboken binding runtime | Both |

The Stable archive contains no Qt6Pdf.dll; neither archive contains a Qt6WebEngine DLL. Wheel metadata alone is not a shipped-library inventory. Qt Shader Tools is included in the acquisition matrix as a build-dependency investigation, not a claim that its DLL ships.

## Acquisition

The source evidence workflow retrieves vendor archives and verifies the official SHA-256 record before retaining the original bytes and license-member inventory in temporary Actions artifacts. QtBase and PySide checksums are recorded from vendor metadata, not independent cryptographic provenance. Other modules require live vendor checksum verification, not independent pinned provenance. A failure in one matrix job does not stop the others.

- https://download.qt.io/archive/qt/6.12/6.12.0/submodules/
- https://download.qt.io/official_releases/QtForPython/pyside6/PySide6-6.12.0-src/
- https://www.qt.io/development/open-source-lgpl-obligations

A successful download is evidence of source availability only. Determine exact wheel edition, source revision and build configuration, any downstream patches, applicable third-party source and notices (including PDFium for Beta), and distributor-controlled durable corresponding-source delivery. Do not claim the source archives fully correspond to the delivered binaries before this mapping is established. Do not publish review artifacts as approved release assets.

## Replacement and installation review

The app uses dynamically loaded Qt libraries, but this alone is not proof of LGPL compliance. Validate user ability to replace and run compatible rebuilt libraries, retain unmodified originals for recovery, and document required compiler/ABI, dependencies, installation paths and build instructions. Do not suggest arbitrary DLL mixing as a security fix. The MIT application source remains separate. Source acquisition does not resolve actual advisory applicability, native Windows acceptance or signing/authenticity.

No product code, candidate hash, tag or release state changes in this branch.

See [OpenSSL notice evidence](OPENSSL_NOTICE_EVIDENCE.md) for the exact frozen binary review and retained upstream license. Corrected source-acquisition workflow uses official alternate archive locations and supports hash-only checksum records.
