# First Stable instructor delivery — acceptance-driven, no fixed version/date

Owner clarification 2026-11-26 supersedes the earlier 2026-11-30 target and any mandatory v1.0.0 commitment: there is no fixed Stable release date or version number. Publish the first Stable only when the exact source, full regression, supported security-patched dependencies, redistribution/source obligations, native Windows UX, clean/pre-equipped installation, and verified assets are accepted. Do not mislabel an internal candidate or Beta as Stable. Keep release stabilization and next-generation development independent; do not block a valid academic handoff on full 13-chapter coverage, arbitrary wiring or other next-generation scope. If Stable gates remain open, provide only a transparently labeled verified Beta/RC with known blockers.

## Exact baseline (before metrics-tool commits)

Repository created 2026-11-24 11:37:21 UTC. Latest measured development commit dated 2026-11-26 09:52:26 UTC; elapsed calendar time 46 h 15 min 5 s, not active effort.

| Metric | Installable beta ecb6647c38a93a4eb9c2171c99c10392abd15e72 | Development 3331f584432445cf3eab87cb6ef505d35d6bd6b6 |
|---|---:|---:|
| Product/tool Python files | 106 | 138 |
| Product/tool Python physical lines | 13,785 | 17,616 |
| Test Python files | 68 | 100 |
| Test Python physical lines | 5,701 | 7,732 |
| Total Python physical lines | 19,486 | 25,348 |
| Total tracked files | 247 | 341 |
| Markdown files | 50 | 65 |

Method: complete Git tree at each exact SHA; initial root 4c4b458ed8679fc10dca96032eb76144abb358d5 had no Python. Count additions for nonzero Python files from root compare, retrieve and count all missing/zero-diff Python blobs directly; reuse counts only for matching blob SHA. Physical lines include comments and blanks, no Markdown, samples, installer/config or dependency code. New source_metrics.py reproduces counts on a Git checkout using committed blobs; seven local fixture tests passed, exact source and test blobs 33cb68d0d0ab7835e3f6b1e9a3d420671968ff15 and 4e942fc0eabadaaf60293e36921d074f469f0998. It was not run against full remote checkout locally because GitHub DNS is unavailable.

## Acceptance gates — no LOC target

- [x] Exact beta builds, portable and installer generated (run 45786384159), automated install/uninstall/launch smoke passes.
- [x] Downloaded beta assets and manifest/checksums verified independently.
- [ ] Exact beta regression on Windows and Ubuntu (run 45786384171; Windows executing pytest, Ubuntu queued at inspection).
- [ ] Native Windows acceptance on disposable VM/actual desktop: fresh install, launch, offline translation, open/save/export RTL/ASM, bilingual restart and keyboard, error behavior, no data loss, uninstall; validate supported screen/DPI settings and course demo. Review and record third-party redistribution obligations and unsigned warning. Signing status is explicit; never bypass OS trust warnings.
- [ ] Merge only accepted candidate source; assign the next appropriate Stable version after scope and acceptance are confirmed. Version, release notes, build metadata and installer names must agree. Never rename a Beta EXE.
- [ ] Rebuild exact stable candidate and rerun relevant/full acceptance tests on that exact commit; verify new installer/portable, checksums, manifest, actual upgrade if claimed. Do not imply all new development features ship.
- [ ] Publish release (or approved instructor delivery package) with verified stable assets, MIT and third-party notices, independent academic translator, bilingual quick start, known limitations, exact SHA and test evidence. Public release requires redistribution clearance. GitHub connector cannot publish releases directly; repository owner can create release/upload assets through GitHub UI.
- [ ] Instructor demo rehearsal and handoff, including raw input/output files and single Python converter explanation. If stable acceptance fails by deadline, deliver transparently labeled verified beta/RC plus known blockers, not a false stable label.

## Event-driven checkpoints (no calendar commitment)

1. Resolve the exact-head cross-platform regression and rebuild evidence.
2. Obtain supported patched PySide/Qt and OpenSSL dependencies; pin and verify their provenance.
3. Complete module-specific redistribution/source obligations and competent review.
4. Perform clean and pre-equipped Windows install, upgrade, offline, bilingual, scaling, save/export and uninstall acceptance.
5. Merge only accepted source, build the chosen Stable version from that exact commit, reverify installer/portable hashes and publish through authorized release tooling.

A delayed runner, unavailable upstream security patch or failed acceptance gate pauses publication; it does not authorize lowering the bar. Keep the academic translator separately downloadable and provide an honestly labeled Beta/RC if the Stable gate is not yet satisfied.

Next-gen scope remains tracked by #23, including .mano, composable labs, updater and all textbook sections. The new development features are not automatically promoted to v1.0.0. Release #4 and #22 are the authoritative active release records.
