# Independent byte-level verification of notice-corrected candidates

2026-11-28. Review-only; no distribution approval.

Compared actual downloaded inner Portable ZIP contents, not just GitHub metadata. Both old and new archives passed ZIP CRC. For every file, independently recomputed SHA-256 and size and compared against the delta manifest.

| Channel | Original artifact | Remediation artifact | Identical files | Added files | Removed | Modified |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| Stable | 15221357225 | 15252792001 | 294 | 238 | 1 | 1 |
| Beta | 15220621215 | 15253894494 | 339 | 238 | 1 | 1 |

Both sets of added/removed/modified paths, all recorded before/after file lengths and hashes, and unchanged counts matched the actual archive contents exactly. The only removed file was `_internal/PySide6/opengl32sw.dll`; the only modified file was `third-party-notices/inventory.json`. All other pre-existing files, including the application executable, are byte-identical. Both artifacts contain PASS in their portable Windows and offscreen smoke files. Hosted Setup install/smoke/uninstall passed in [run 46114555414](https://github.com/mohammadrezamie/mano-studio/actions/runs/46114555414).

Reuse this exact evidence rather than rerunning application tests solely because notice files were added. Removing the optional software OpenGL fallback still requires native graphics acceptance; changing any executable or runtime DLL requires a new exact-candidate assessment. OpenSSL security disposition, Qt source correspondence and license compliance, independent native desktop acceptance and final publication remain open. Do not infer approval from this report.
