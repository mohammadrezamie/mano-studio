# First beta candidate — delivery checklist

Internal test build, not a published release. Target Windows 10/11 x64. Version in this commit: 1.1.0-dev.1. Proposed first public version: v1.1.0-beta.1; separate Stable candidate: 1.0.0. The public Beta must remain semantically ahead of Stable; publish only after every Beta gate passes and the owner approves.

## Live acceptance checkpoint — 2026-11-27
- [x] Parent PR #36 focused integration run passed 702 checks (622 core, 60 Qt, 20 workspace) on exact head `2b19fe4f`.
- [x] Parent PR #36 visual acceptance passed on exact head with 36/36 unique images matching the visual manifest.
- [ ] Child PR [#37](https://github.com/mohammadrezamie/mano-studio/pull/37) full Windows/Ubuntu regression and exact-head Windows installer workflows.
- [ ] Independently inspect #37 portable and Setup artifacts, SHA-256 files, PE inventory, raw notice inventory, installed-payload comparison, OpenSSL runtime flags and redistribution-preflight output.
- [ ] Resolve Qt LGPL/GPL corresponding-source and module-specific notice obligations; wheel hashes and automated inventory are not legal approval.
- [ ] Clean-machine/native Windows keyboard, scaling, Persian, file-workflow and offline acceptance; signed installer; owner approval.
- No public Beta tag/release is confirmed. Do not treat parent PR focused tests or the visual artifact as package acceptance.

## Source and scope
- Standalone RTL-to-ASM source; 25 documented instruction templates; provisional classroom dialect.
- Persian/English, file workflow, builder, symbol pad, offline help, settings, three themes, optional glass and motion.
- Approved M-chip, localized About and real event-driven graphics.
- Ten bilingual CPU sample programs, read-only timing-cycle inspector, existing chapter exercises and optional labs. Representative coverage is not full textbook coverage.

## Release gates (not complete)
- [ ] Exact integrated Windows/Ubuntu tests and glyph preflight pass.
- [ ] Verify the exact 36-image bilingual evidence matrix: 2 locales × 3 themes × 2 glass styles × 3 user-facing surfaces (1360×900 workspace, 1024×768 workspace, splash). No in-app academic source-viewer screenshots are expected; About/credits must also be checked in native Windows acceptance.
- [ ] Portable and installed Windows x64 smoke tests, installer removal, academic source checksum and candidate manifest.
- [ ] Native Windows keyboard, scaling, Persian and file workflow acceptance. Confirm instructor-specific RTL dialect and attribution.
- [ ] Redistribution/license and signing review; communicate unsigned status if applicable, never imply trusted signing.
- [ ] Confirm final version, exact candidate SHA and release checksums, owner approval. Build again if version or source changes.
- [ ] Publish only explicitly marked GitHub prerelease with setup, portable, hashes and honest limitations.

No automatic publication. No new feature scope. PR #36 integrates the exact reviewed heads of #25, #32, #33 and #34 on the current develop/next-beta baseline; each source PR remains available for diagnosis. PR #36 stays draft until combined tests and Windows visual acceptance pass.
