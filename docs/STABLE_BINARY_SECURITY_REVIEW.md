# Stable — binary security and redistribution review

Observed 2026-11-26 from actual internal v1 portable artifact 15106817148, source 3ed419e3a37d9e233a4a908c08f9eccbbe80bf83. This is a release blocker review, not a legal determination, vulnerability exploitability assessment or new build. Original archive unchanged.

## Inventory classification

All 112 binary paths classified by filename/path for further provenance work. These categories are hypotheses to reconcile with exact upstream source/SBOM, not license grants.

| Group | Count |
|---|---:|
| Microsoft runtime candidates | 53 |
| Qt plugins | 22 |
| Qt module DLLs | 13 |
| Python runtime / stdlib extensions | 10 |
| PySide bindings | 6 |
| OpenSSL candidates | 4 |
| Shiboken bindings | 2 |
| Software OpenGL candidate | 1 |
| ManoStudio bootloader | 1 |
| Total | 112 |

MSVCP140.dll, VCRUNTIME140.dll and VCRUNTIME140_1.dll occur with respectively two, three and three different hashes. Do not deduplicate by filename. Map to source package and applicable redistribution terms; Qt third-party SBOM, software rendering and image/PDF codec notices must be reconciled with actual packaged components.

## P0: obsolete TLS dependency

Python runtime recorded as 3.12.10. Binary strings and ordinary PE import inspection using objdump -p on all 112 binaries (no DLL executed) show:

- `_internal/libcrypto-3.dll`: embedded OpenSSL 3.0.16, 11 Feb 2025; SHA-256 ccfffddcd3defb8d899026298af9af43bc186130f8483d77e97c93233d5f27d7.
- `_internal/libcrypto-3-x64.dll`: embedded OpenSSL 3.5.9, 29 Sep 2026; SHA-256 d51f2b081e5ac0f94c2bf15650a6b55cf48da1de8c313c9f90003d9ed08ccc9e.
- `_hashlib.pyd` directly imports libcrypto-3.dll; `_ssl.pyd` directly imports libcrypto-3.dll and libssl-3.dll. Each libssl variant imports the matching libcrypto name. The other SSL variant is not proven unused: dynamic plugin loading is not captured by this ordinary-import check.
- OpenSSL upstream confirms public support for 3.0 ended September 7, 2026. Later security advisories also need review for 3.5.9, including Nov 24 advisories. Do not claim an affected app path or exploit without analysis. Offline core does not eliminate risk of the explicitly invoked HTTPS update feature.

## Remediation / acceptance

1. Keep current #24/#22 source and build evidence intact. #26 pinned-build run 45804344694 remains an internal diagnostic; do not publish it even if green until this issue is resolved.
2. For the next candidate select a maintained Windows CPython with a supported OpenSSL runtime. Python 3.14.10 is a documented Windows-binary candidate, not approved yet. Python 3.13.16 moved Windows builds to OpenSSL 3.5.9, but do not assume latest 3.13 source-only fixes are in an older Windows binary. Verify wheel ABI, PyInstaller, Python version, actual ssl.OPENSSL_VERSION and archive DLL versions. Review the recent OpenSSL advisories and obtain patched official binaries or document justified applicability/mitigation. Do not swap DLL filenames or mix builds by hand.
3. Pin and verify exact upstream provenance/approved hashes before publishing; use source/build SBOM and actual package metadata to reconcile Python, Qt, Mesa, OpenSSL, Microsoft and other notices. The existing #26 gate is heuristic evidence and does not approve security or legal redistribution.
4. Re-run both full regression platforms, exact portable and installed smoke, explicit update TLS workflow, checksum validation and native Windows acceptance on the new candidate. No publication or stable approval until evidence.

## Native acceptance checklist (manual Windows)
Record OS/build, architecture, display scaling, exact source SHA, installer SHA-256 and reviewer. For a clean non-admin account, install and launch offline; exercise en/fa at 100%, 125%, 150% and compact layout; validate readable Persian and LTR technical code; test keyboard focus, file import/save, invalid RTL preserves existing output/file, all academic demo instructions, copied/exported independent Python source, language/theme persistence, reduced motion, on-screen RTL pad, uninstall/reinstall, and explicit update check only after enabling network. Record expected and actual outcomes, failures and screenshots; never mark pass based only on offscreen CI. Verify release assets, notices, publisher identity and download before approval.

## Official references (checked 2026-11-26)
- https://openssl-library.org/post/2026-09-16-eol30/
- https://openssl-library.org/news/vulnerabilities-3.5/
- https://www.python.org/downloads/release/python-31410/
- https://www.python.org/downloads/release/python-31316/
- https://docs.python.org/3.12/license.html
- https://doc.qt.io/qt-6/licenses-used-in-qt.html
- https://doc.qt.io/qt-6/windows-graphics.html
