# Independent exact release-asset verification — 2026-11-27

This checkpoint uses the actual downloaded Actions archive bytes, not source-only or prior candidate results.

| Channel | Source commit | Setup bytes / SHA-256 | Portable bytes / SHA-256 |
| --- | --- | --- | --- |
| Stable 1.0.0 | `926272ff0ebfa4731cfb0b00c149c7e12b4d5a56` | 31,001,449 / `3525135132eaabe6039e3c543911ac6429e71e453b53792968e91fb1a142ef9c` | 44,996,332 / `bc93823dbea393f17464886abeef406defda22e4151dbaab82293928eae3271e` |
| Beta 1.1.0-beta.1 | `2dd55994d36f2596dd3d17ea54dd3c3e43829ae2` | 31,098,046 / `8fcd72cc280892de6c76c76d555ab4c6601b9e9753cb13157ca0c01ee127a0bc` | 45,109,279 / `b6a9e2c0fa4014ce505d68e639a328f6ec193b98655c2f123a93365d3b523109` |

All four outer artifacts (15221272367, 15221357225, 15220751219, 15220621215) CRC and SHA-256 match GitHub API evidence. Both inner portable ZIP CRCs pass. Stable 106/106 and Beta 104/104 binary inventory paths, sizes and hashes match. GNU objdump -p successfully read all 210 ordinary PE import tables; no references to Qt QML/Quick, Multimedia, WebEngine, PDF or Virtual Keyboard were found. Neither archive has binaries named for these groups. Ordinary imports are not delay-import or runtime tracing.

## Academic deliverable independently executed

Both extracted rtl_translator.py files are byte-identical (SHA-256 `0a2540403aeced6b6d31a1b79c67e26c489a0c48008537d87915ee5d52c62dec`). Executed only this exact file in a temporary directory via local Python 3.13.5 `-I -S` with Persian file paths and BOM/CRLF input. Independent matrix: 7 memory instructions × 4096 addresses × 2 addressing modes, plus 18 fixed instructions × 3 spelling variants = **57,398 valid instruction conversions passed**. All 14 out-of-range instruction/mode cases rejected without altering prior output. AST imports are standard library only. This validates the shared classroom core, not native GUI, complete suite or actual installed Python 3.14.10 environment.

## Security applicability evidence

Both frozen CArchive/PYZ payloads inspected without executing their Windows binaries (247 Stable and 285 Beta nonempty Python module/script records, including standard library). Raw decompressed marshal byte-string scan found no QCborValue, QCborArray, QCborMap, QCborStreamReader, QNetworkAccessManager, QNetworkRequest, QNetworkReply, QWebSocket, VectorImage, QSoundEffect, QAudioDecoder, VERIFY_CRL_CHECK, DANE, PKCS7 or QUIC token. QtQuick/QtMultimedia/QtWebEngine strings occur only in the PySide6 package initialization metadata; the native modules are absent. Both update_service records contain urllib.request and urlopen; Beta also includes update_download. This is static token evidence, not exhaustive dynamic reachability or a penetration test.

- CVE-2026-123706 (VectorImage/Qt Quick), CVE-2026-118968 (WAV/Qt Multimedia): affected component absent in both actual lean payloads. No evidence of affected application use. Reassess if reintroduced.
- CVE-2026-105924 (QCborValue to JSON), CVE-2026-116337 (Qt HTTP response processing): affected Qt6Core/Qt6Network libraries present, no explicit affected API token found in frozen Python records. Not cleared; native internal paths may exist. Keep security review open.
- OpenSSL 3.5.9 runtime evidence unchanged; scheduled future fix does not imply availability today. No version substitutions.

Official sources: https://www.qt.io/blog/security-advisory-cve-2026-123706-qt ; https://www.qt.io/blog/security-advisory-cve-2026-118968-denial-of-service-vulnerability-in-wav-audio-decoding-impacts-qt ; https://www.qt.io/blog/security-advisory-cve-2026-105924 ; https://www.qt.io/blog/security-issue-cve-2026-116337 .

## Remaining publication gates

Exact full regression 46048466661, draft refresh 46050324491, authenticity workflow 46050465305, independent visual/native review, retained corresponding source/build configuration and redistribution review. Upstream Qt for Python build guide https://doc.qt.io/qtforpython-6/building_from_source/index.html and licensing obligations https://www.qt.io/development/open-source-lgpl-obligations ; neither source tarballs nor wheel matching prove full source correspondence. Do not treat unsigned binaries as Authenticode-signed; no public release approval. No frozen runtime change.
