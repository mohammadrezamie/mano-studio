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

## Review of the 23 collector warnings — 2026-11-28

The original artifact 15247465980 retained 235 files, including 87 attribution JSON documents, from five source archives. Inspected every warning's original attribution and nearby notice files. All 23 fall into two categories: 7 documents with raw unescaped newlines in JSON strings (original bytes retained, relaxed parser can read them), and 16 attribution entries with no singular LicenseFile. The latter are not necessarily missing licenses. Five of the 23 warnings refer to test fixtures or PySide examples (two QtBase SBOM fixture entries and three PySide example warnings), not evidence of a shipped runtime obligation. Keep those source notices, but do not count them as runtime blockers without evidence of inclusion.

Concrete collector defect: libjpeg declares LicenseFiles (plural) containing LICENSE and ijg-license.txt, plus CopyrightFile. The first archive omitted ijg-license.txt because its basename did not match the broad filename heuristic. Corrected the collector in 4a1941dc93a4adc068dad2394004d95feda126b0 to parse singular/plural license and copyright fields and retain explicit paths. A local scan of all relaxed-parsed original entries found this one missing explicit referenced file in the original notice archive. New collection run 46105057247; do not treat it as complete until verified. Existing remediation pilot 46104979539 uses the older pinned review archive and is an experiment only, not an approved package.

Other runtime entries with no explicit file (e.g., Emoji Segmenter, Unicode UCD/CLDR, MD4/MD5, SHA-1, SipHash, SQLite, Wintab, tl::expected, Apache Tika, SPIRV-Cross) need applicability and text mapping rather than automatic rejection. The archive already contains QtBase LICENSES/Apache-2.0.txt, CC0-1.0.txt, Unicode-3.0.txt and LicenseRef-SHA1-Public-Domain.txt. A matching generic text does not replace any component-specific copyright or notice. No independent legal, security, or native acceptance decision is claimed.


## Explicit license identifier crosswalk — verified against the first archive

Independent local inspection of artifact 15247465980 resolved all 16 missing-singular-LicenseFile warning entries to actual license text files in the same upstream module's LICENSES directory, with original attribution and copyright data retained. This is a mapping of existing bytes, not a determination that a component is shipped or that all obligations are satisfied.

| Attribution | License text(s) retained |
| --- | --- |
| Emoji Segmenter; Apache Tika MimeType Definitions | QtBase Apache-2.0.txt |
| LibJPEG-turbo | QtBase IJG.txt and BSD-3-Clause.txt |
| MD4; MD5; SipHash; tl::expected | QtBase CC0-1.0.txt |
| SHA-1 | QtBase LicenseRef-SHA1-Public-Domain.txt |
| SQLite | QtBase blessing.txt |
| Wintab API | QtBase LicenseRef-Lcs-Telegraphics.txt |
| Unicode UCD and CLDR | QtBase Unicode-3.0.txt |
| SBOM test parent / child | QtBase MIT.txt / BSD-3-Clause.txt |
| Selected Material Icons (example) | PySide Apache-2.0.txt |
| SPIRV-Cross | QtShaderTools Apache-2.0.txt and LicenseRef-MIT-Khronos-old.txt |

**Correction to the preceding omission finding:** the specific libjpeg/ijg-license.txt path was absent in the first archive, but the exact same text was already retained as QtBase LICENSES/IJG.txt (SHA-256 1cb448f5e2e6d3aca60943f4eee1a04675628dc0266a074a42bc1560ebc28d61). The collector fix still preserves all explicitly referenced paths. Do not characterize this as missing IJG license text. All 16 SPDX-like identifier mappings resolve, including the two compound AND expressions; seven malformed original JSON documents remain preserved. No legal review or exact build-configuration signoff inferred.

The frozen original preflight JSONs independently inspected in artifacts 15221357225 and 15220621215 each contain exactly two redistribution flags (Qt corresponding source/relink, Qt Image Formats notice/corresponding source), and three OpenSSL runtime review flags (two libcrypto binaries and build SSL version). These are separate from the notice-collector warnings; none has been silently cleared.
