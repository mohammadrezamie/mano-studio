# QtBase third-party attribution mapping — exact lean candidates

2026-11-28. Review of the actual portable archives (Stable artifact 15221357225; Beta 15220621215) and the checksum-verified QtBase 6.12.0 source in source review artifact 15220635288. Both have the same Qt/PySide runtime path list; this is not a claim that all binary hashes or all upstream build options were independently rechecked here.

## Concrete observations

| Runtime binary (under _internal/PySide6) | Case-insensitive ASCII/UTF-16LE tokens found in Stable | Candidate upstream attribution path in QtBase source |
| --- | --- | --- |
| Qt6Core.dll | PCRE2, 10.48 | src/3rdparty/pcre2/qt_attribution.json |
| Qt6Core.dll, Qt6Gui.dll, Qt6Svg.dll | zlib, 1.3.2 | src/3rdparty/zlib/qt_attribution.json |
| Qt6Core.dll, QtCore.pyd | BLAKE2 | src/3rdparty/blake2/qt_attribution.json |
| Qt6Gui.dll | HarfBuzz | src/3rdparty/harfbuzz-ng/qt_attribution.json |
| Qt6Gui.dll, platform plugins qdirect2d/qminimal/qoffscreen/qwindows | FreeType | src/3rdparty/freetype/qt_attribution.json; src/gui/painting/qt_attribution.json |
| Qt6Gui.dll | libpng, 1.6.58 | src/3rdparty/libpng/qt_attribution.json |
| Qt6Gui.dll | D3D12 Memory Allocator | src/3rdparty/D3D12MemoryAllocator/qt_attribution.json |
| imageformats/qjpeg.dll and qtiff.dll | libjpeg, 3.2.0 | src/3rdparty/libjpeg/qt_attribution.json |
| platforms/qdirect2d.dll and qwindows.dll | wintab | src/3rdparty/wintab/qt_attribution.json |
| opengl32sw.dll | Mesa 11.2.2, LLVM 3.6.2, zlib | Separate Mesa disposition; not QtBase source correspondence |

A token is not proof of static linking, exact version, executable reachability or absence of other components. Version strings are independent token hits, not parsed version attestations. The QtBase source attribution JSON declares PCRE2 10.48, zlib 1.3.2, HarfBuzz-NG 14.5.0, FreeType 2.14.3, libpng 1.6.58, libjpeg-turbo 3.2.0, D3D12 Memory Allocator v3.1.0. Source paths and reported versions do not establish vendor build configuration.

Current frozen notices contain Qt LGPL/GPL texts, wheel metadata, Python/PyInstaller and OpenSSL notices and the Qt Image Formats attribution subset; they do not contain a separately named QtBase third-party attribution directory. The retained QtBase source archive itself includes the upstream attribution and license files. A release review must determine applicability and include all required notices in a reviewed distribution, not just this shortlist. In particular, do not infer coverage of FreeType, PCRE2 exceptions, libjpeg, D3D12 or platform components from the generic Qt license text alone. No public release approval.

## Practical disposition

1. Retain the complete checksum-pinned upstream QtBase source archive and generate a review inventory of its third-party attribution entries with license file references. Do not remove platform-specific entries based solely on token searches.
2. Compare the exact vendor wheel build configuration against attribution entries, including embedded third-party code; obtain missing correspondence information from upstream when unavailable.
3. Review the notices for the exact final package and the separate Mesa fallback decision. The QtSvg replacement experiment proves one practical library replacement, not complete source correspondence.
4. Do not replace already-verified executable bytes just to add unrelated features. If an actual notice omission requires a new package, identify it explicitly, verify changed payload scope and perform exact acceptance.

References: https://www.qt.io/development/open-source-lgpl-obligations ; https://www.qt.io/development/download-open-source ; https://doc.qt.io/qtforpython-6/licenses.html . Independent native desktop acceptance, final security and redistribution review remain open.
