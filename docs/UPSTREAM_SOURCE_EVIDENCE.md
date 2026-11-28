# Current frozen-candidate source scope — 2026-11-28

This checkpoint supersedes the older candidate inventory below. Current Stable source 926272ff0ebfa4731cfb0b00c149c7e12b4d5a56 and Beta source 2dd55994d36f2596dd3d17ea54dd3c3e43829ae2 have 43 identical Qt/PySide/Shiboken binaries per channel, verified against the published Essentials/Shiboken wheels. Current portable artifacts 15221357225 and 15220621215 do not contain the previously shipped Qt PDF, QML/Quick, or WebEngine runtime libraries. Do not block on WebEngine/PDF source correspondence for binaries no longer shipped. The prior WebEngine/PDF wheel-source discussion is relevant only to those excluded components (https://forum.qt.io/topic/165231/corresponding-source-code-and-third-party-notices-for-pyside6-webengine-pdf-6-12-0.140-windows-wheels/4).

- Six source archives and wheel-origin evidence retained in artifact 15220635288, outer SHA-256 e8ad1e1e7c1ca7b7e5e793e54007fe85ad1e3ed95b215c4dba507c8feb9ef129; independently checked all archive hashes.
- QtBase, QtSvg, QtImageFormats and PySide/Shiboken remain in the native source review. Retain QtDeclarative and QtShaderTools evidence conservatively until build-dependency assessment is finished. Do not assert all six are shipped.
- QtSvg modified-library replacement succeeded on both exact frozen candidates; this does not establish all-library native compatibility or exact vendor configuration.
- Accessible-notice Stable pilot 15252792001 adds 236 readable notices and removes the optional Mesa fallback, with hosted installation/smoke success. It remains review-only pending independent graphics/native acceptance and final security/source review. Original frozen assets are unchanged.
- Remaining source review concerns the actual retained modules, corresponding build inputs, notices, durable source access and replacement instructions. PYSIDE-3485 is a relevant upstream lead, not verified legal clearance (https://qt-project.atlassian.net/browse/PYSIDE-3485). A forum follow-up acknowledges a binding-tag clarification but does not independently establish the exact configuration of the retained native Qt libraries.

No release approval is inferred. Do not rebuild or retest merely because this historical scope has been corrected.

## Qt translation catalog scope — exact Stable archive

The inner Portable archive in artifact 15221357225 contains 99 .qm files under PySide6/translations. Independently enumerated the ZIP members and compared catalog stems with official qttranslations v6.12.0 commit 2811457ceff8f0c24a1c4d14f947a283a17239d0: 96 have matching .ts files under translations/. The three remaining English catalogs (qt_en, qtbase_en, qt_help_en) correspond to the upstream build's generated empty English TS mechanism (generate_empty_ts_file in translations/CMakeLists.txt). This establishes source-name coverage, not proof of identical compiled catalog content or redistribution approval. Retain the official archive, license evidence and relevant build scripts; verify the source archive checksum in run 46121607338. No further catalog discovery workflow is necessary.

---

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
