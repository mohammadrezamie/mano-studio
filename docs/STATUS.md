# Development status — 2026-11-24

Active checkpoint: draft PR #9, feature/desktop-workspace. Continue this branch and inspect Actions before merging. No stable release or v1.0.0 tag; owner approval after classroom review is mandatory. See RELEASE_POLICY.md.

## Completed and verified history
- Standalone Python RTL translator and catalog cover 25 named instructions / 32 documented forms; prior Linux tests: 64 passed.
- Desktop preview: three input modes, Persian/English, Light/Dark/Night, persistent settings, file operations, diagnostics, source viewer, numbered editor and error highlights. Initial CI failed on missing libEGL (run 45388211041); fixed runtime dependencies, both platforms passed run 45388377303. Screenshot/test workflow 45388500498 succeeded before later changes.
- Mano Glass Qt/QPainter design and four-instruction animated educational demo are implemented on branch. Not native Apple refraction or general simulator. Global glass/reduced-motion preferences and manual-only update service implemented with tests; latest complete CI not yet verified. All core features offline, no global online mode, startup requests or telemetry.

## Current installer checkpoint
Added requirements-build.txt, installer/build.ps1, installer/mano-studio.iss, installer/collect_notices.py and installer/smoke.ps1. PyInstaller onedir includes readable rtl_translator.py, examples, docs and license; Inno Setup x64 per-user install, optional desktop shortcut and uninstaller. main.py --smoke-test checks real frozen UI translation, invalid-input rejection and bundled source/example. Windows Actions workflow builds and tests, installs, smoke-tests, uninstalls and uploads development installer plus SHA256 as a temporary artifact only; no public release or stable tag. Build result not yet confirmed. Installer unsigned; review third-party Qt redistribution obligations and pin verified build dependencies before public distribution.

## Next work
1. Inspect current Windows installer workflow and test logs; resolve failures and inspect actual screenshots.
2. Test on independent clean Windows machine (no Python), verify no network dependency, source viewer, install/uninstall and settings; refine visual polish, autocomplete and academic attribution as verified.
3. Class target: 2026-11-30 to 2026-12-06, explicitly marked 0.x beta only, subject to verification. Current version 0.3.0-dev. Issue #4 packaging, #2 UI, #10 comfort/update preferences remain open. Full simulator #3 and reverse #8 deferred if needed.
