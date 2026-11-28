# Qt Image Formats supplemental notices — internal release candidate

This supplement records notices for image-format plugins present in the Windows x64 Qt 6.12.0 runtime. It is not a legal opinion, a commercial Qt license, a complete corresponding-source offer, or approval to redistribute.

The qicns, qtga, qtiff, qwbmp and qwebp plugin implementation sources in Qt Image Formats 6.12.0 declare `LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only`. Their plugin CMake files declare BSD-3-Clause. The exact Qt LGPL/GPL license texts are provided in the parent `qt-license-texts` directory. The BSD license text is reproduced verbatim from the upstream Qt Image Formats source archive.

Qt's upstream attribution metadata identifies libtiff 4.7.2 in qtiff when no system libtiff is found, and libwebp 1.6.0 in qwebp when no system libwebp is found. Their upstream license texts are included here conservatively. The frozen wheel's build configuration and whether these components were statically embedded or linked against system libraries must be confirmed from the exact PySide wheel build configuration before distribution.

Upstream source archive:
- Qt Image Formats 6.12.0: https://download.qt.io/archive/qt/6.12/6.12.0/submodules/qtimageformats-everywhere-src-6.12.0.tar.xz
- SHA-256: `0943132b5db8de6b6a7f1d162682173e8763c7ed94e80fd39113292845f67762`
- Vendor checksum was verified in GitHub Actions; the archive and plugin/license mapping are retained as review evidence.

The source archive contains the exact plugin source files and embedded third-party source trees for this Qt release, but exact wheel build revisions, build flags, patches, complete source correspondence, replacement/relink instructions and independent legal review remain open. Do not infer redistribution approval from these files.
