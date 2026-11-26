# Release acceptance checkpoint — 2026-11-26

This evidence ledger is separate from the frozen release branches. The owner targets Monday 2026-11-30 for v1.0.0 instructor delivery. Internal candidates are not public releases. Full-book coverage is not a delivery gate.

| Evidence | Beta #22 | v1 #24 |
|---|---|---|
| Exact candidate SHA | `ecb6647c38a93a4eb9c2171c99c10392abd15e72` | `3ed419e3a37d9e233a4a908c08f9eccbbe80bf83` |
| Windows build workflow | [45786384159](https://github.com/mohammadrezamie/mano-studio/actions/runs/45786384159) — success | [45798904733](https://github.com/mohammadrezamie/mano-studio/actions/runs/45798904733) — success |
| Full regression | [45786384171](https://github.com/mohammadrezamie/mano-studio/actions/runs/45786384171) — both Windows and Ubuntu pytest in progress | [45798904930](https://github.com/mohammadrezamie/mano-studio/actions/runs/45798904930) — Ubuntu pytest in progress; Windows queued |
| Native Windows user acceptance | Pending | Pending |
| Redistribution / public assets | Pending | Pending |

## Exact v1 installer workflow evidence

Job 139836643064 completed successfully: recorded source, installed dependencies, configured Windows fonts, passed glyph preflight, packaging/credits tests, focused instructor UI, actual capture, portable build and smoke, Inno Setup build, install/run offline/uninstall smoke, dependency recording, SHA-256 and candidate manifest validation. This is automated Windows evidence, not a personal native UI review.

Artifacts listed and not expired at observation (sign-in may be required; use the run's Artifacts section):

| Artifact | ID | Archive bytes |
|---|---:|---:|
| ManoStudio-Windows-x64-development | 15107145149 | 35115217 |
| ManoStudio-Windows-x64-portable-development | 15106817148 | 50707260 |
| installed-smoke-report | 15106282672 | 296 |
| ManoStudio-v1-instructor-preview | 15105499016 | 2989313 |

Sizes above are CI artifact archive sizes, not individual installer sizes. This checkpoint verifies workflow metadata and artifact inventory only; it does not independently download, rehash or inspect the v1 artifact pixels.

## Acceptance sequence

- [ ] Confirm each complete regression run concludes success and inspect JUnit counts, warnings, logs and preview artifacts for the exact SHA. Do not substitute the focused packaging smoke tests for the full matrix.
- [ ] Download the candidate artifacts; validate manifest source/version, expected portable and setup SHA-256, executable/source inclusion, dependency and redistribution notices. Keep the artifact ID and digest in the release record.
- [ ] On a clean Windows 10/11 x64 account, install without assuming development tools are installed; launch offline, test English and Persian at 100% and 150% scaling and 1024×768, check all three themes, reduced motion, glass-off, focus order, keyboard operation, no clipping, and persisted preferences after restart. Check uninstall; verify user documents are not removed.
- [ ] Rehearse the academic assignment: import RTL, convert to expected ASM, export, open exported text, exercise each input mode, demonstrate error rejection without replacing a valid output; run the independent `rtl_translator.py` with a standalone Python interpreter and compare output. Keep unsupported syntax clearly documented.
- [ ] Verify PR #24 still points to the tested revision. If selectively promoting a visual improvement, create a new exact candidate and repeat the relevant tests, packaging and acceptance. Do not merge next-generation features wholesale.
- [ ] Obtain required native and redistribution acceptance; reconcile documentation and merge only a verified candidate. Publish correctly versioned assets, checksums and release notes only through an authorized publishing route; verify final download links. If v1 gates remain open, use an honestly labeled verified beta/RC fallback rather than relabeling its assets.

## Independent next-generation track

PR #25 at `1cc1f08ceed8b4ff1dfa75342b2df8b03dc0cb92` targets develop/next-beta; typography and isolated instructor demo improvements are proposed. Its dedicated visual-polish workflow triggers on branch push; the available commit-workflow listing filters to PR-triggered runs, so absence there is not evidence that the push workflow failed or never ran. Inspect Actions directly before promotion. Earlier next-beta integration job 45796017571 was cancelled; no successful result inferred. Do not restart either frozen release candidate for documentation edits.

## Handoff

See [#4](https://github.com/mohammadrezamie/mano-studio/issues/4), [#23](https://github.com/mohammadrezamie/mano-studio/issues/23), [#24](https://github.com/mohammadrezamie/mano-studio/pull/24), [#25](https://github.com/mohammadrezamie/mano-studio/pull/25), and [#20](https://github.com/mohammadrezamie/mano-studio/pull/20) for current state. The next priority is regression evidence and native acceptance, with independent development on its own branch. No tag/release operation was performed.

## Independent artifact verification — same checkpoint

Downloaded all four listed archives and verified archive CRCs; nested portable archive contains 321 entries and also passes CRC. Exact source revision in both commit.txt files and manifest: 3ed419e3a37d9e233a4a908c08f9eccbbe80bf83. Independently recalculated lengths and SHA-256, matched both sidecar digests and manifest:

| Actual asset | Bytes | SHA-256 |
|---|---:|---|
| ManoStudio-v1.0.0-Windows-x64.zip | 50915675 | 1b7860eaf818f831050fd2672007f992638da3cede0ab328d7e267257b337839 |
| ManoStudio-Setup-v1.0.0-x64.exe | 35951004 | 703548ac7f8f7e5f5414195dd6abc66f860c8880903ce0844f31905c36727ea6 |

Manifest reports portable and installed smoke PASS, redistribution review incomplete, native_acceptance=false, public_release=false. Separate smoke archive also contains both PASS records. Portable archive contains ManoStudio.exe, third-party-notices/inventory.json and _internal/rtl_translator.py. Actual extracted academic source SHA-256 0a2540403aeced6b6d31a1b79c67e26c489a0c48008537d87915ee5d52c62dec matches manifest; LF-normalized Git blob dc495ca2bf2484a28fa9aa440e7868ea6932254c matches frozen academic core. Executed actual extracted source with python -I -S and independent four-line RTL sample, output exactly LDA 100 / ADD 101 / STA 102 / HLT (exit 0).

Preview manifest: exact 48-image Cartesian set (two locales, three themes, glass/plain, four surfaces), unique names, all image SHA-256 and dimensions match; all PNGs fully decoded. Inspected contact sheets of 24 compact-workspace/splash captures across all themes and languages, and full-size Persian compact and English large dark glass workspaces. No missing-glyph boxes or major clipping observed in sampled screens. Persian button/footer text is visibly too small relative to English and the editors; #25 is the independent improvement candidate. Offscreen review does not establish native DPI/usability. Full matrix, independent licensing review, native Windows acceptance and publication remain open. This supersedes the earlier metadata-only statement above.
