# OpenSSL advisory applicability review — 2026-11-26

## Scope and disposition

Internal Windows candidate built from #26 bd5d353d4a39583acb92609c7c11d7ff701c6d29 (run 45832491036), installed probe reports Python 3.14.10 and OpenSSL 3.5.9. Two crypto DLL pairs in portable payload; build interpreter previously reported 3.5.0. The current experimental source 1cc06b639ae4eded8f38e210865a9d0def1ecb9f has no new runtime measurement yet. The advisory baseline is 3.5.10 for the 3.5 series. Published Python 3.14.10 and PySide6 6.12.0 pages were rechecked today; no patched compatible replacement established from these pages. Do not substitute a random DLL or silently relax the review threshold.

Source: https://openssl-library.org/news/vulnerabilities-3.5/ (24 November entries, all four marked Low by upstream). The November 10 and 17 entries also need independent review; this table is not an exhaustive vulnerability inventory.

| CVE | Relevant upstream precondition (paraphrase) | Application evidence at inspected revision | Disposition |
|---|---|---|---|
| CVE-2026-84785 | QUIC, acceptance of peer-initiated streams | No such API in inspected updater | No direct updater path identified; other components unreviewed |
| CVE-2026-107494 | QUIC connection ID processing | Standard urllib HTTPS request, not QUIC implementation | Same |
| CVE-2026-121482 | CRL checking during CMS or PKCS#7 signature verification | No CMS/PKCS#7 verification or explicit CRL configuration in inspected updater | Same; verify actual packaged runtime configuration |
| CVE-2026-84786 | DANE-enabled TLS client using relevant TLSA modes | No DANE API or TLSA configuration in inspected updater | Same |

## Actual source inspection

At 1cc06b639ae4eded8f38e210865a9d0def1ecb9f:
- update_service.py blob c2c13bfc441990696c3695e47b331ed86d252255: release_info rejects non-explicit requests before network, standard urllib.request.urlopen with 6-second timeout, fixed GitHub Releases API URL, bounded response read, JSON metadata, not executable asset loading. Uses urllib default TLS configuration; source inspection alone does not establish all operating-system or OpenSSL configuration.
- ui/preferences.py blob 1d1286e856c06299d363df3f63594d082d4ffc33: worker invokes release_info(explicit=True); release page opens via QDesktopServices. Download is browser-based in this stable revision. Beta update code is not assessed here.
- main.py blob 7b87208575cffd4eb18f3c88e6c7602dcfb96078 and ui/workspace.py blob dcefc8965c9eb6774688fda69a72d20195ba966e inspected for updater calls. No global claim of absent network paths or runtime exploitability. Existing offline/smoke tests are separate evidence.

## Next acceptance steps

1. Review full November advisory set, Qt/plugin and bundled dependency exposure, including delayed/dynamic loads and actual TLS configuration.
2. Prefer an official supported patched runtime/wheel; if unavailable, record reviewed alternative or explicit risk acceptance from maintainer after full scope assessment. Do not assume Low severity is approval.
3. Verify actual installed private DLL paths, hashes, loaded SSL version and TLS update behavior on a fresh Windows system; repeat build and applicable exact-revision regressions.
4. Keep offline operation, explicit update check, and browser download policy. Corresponding-source and notices, native Windows acceptance, and release publication remain independent gates.

References: https://www.python.org/downloads/release/python-31410/ ; https://pypi.org/project/PySide6/ ; https://openssl-library.org/news/vulnerabilities-3.5/ . The known installed 3.5.9 is in affected version ranges; this narrow source review does not establish that the application is exploitable or unaffected. No public release approval.
