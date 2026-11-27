# Stable candidate — instructor and visual acceptance

**Status: internal candidate only.** This document defines acceptance for the Stable desktop application. It does not announce a release date or approve publication.

## Academic assignment contract

The instructor-facing deliverable is exactly one independently downloadable Python file at the repository root: `rtl_translator.py`.

- The file contains the RTL-to-Assembly conversion core and its explanatory comments/docstrings.
- It uses only Python's standard library and must run independently of the desktop application.
- The GUI delegates to this file; it must not duplicate the conversion engine.
- The desktop application must not include an in-app source viewer, source editor, source-export helper or academic-source dialog.
- The user downloads and studies the one Python file separately. Optional labs, simulators and visual features remain outside this core file.
- The installer and portable manifest must include the exact same translator bytes as the repository source.

## Application acceptance

- Windows x64 desktop application with a genuine Setup installer and portable build.
- Offline-first operation: no startup network calls or telemetry; only explicit update checks may contact GitHub.
- English and Persian UI, persistent language choice, three themes, glass/plain appearance and reduced-motion behavior.
- Clean install and first launch without separately installing Python, Qt or pip; app-private runtime must not overwrite shared system components.
- Verify ordinary install, pre-equipped machine behavior, reinstall/upgrade, offline smoke and clean uninstall.
- Verify the visible UI at practical window sizes, including Persian typography, RTL layout, readable code editors, splash/credits, keyboard navigation and error guidance.

## Instructor visual evidence

The automated visual evidence matrix contains exactly **36 PNGs**:

- 2 UI languages: English and Persian.
- 3 themes: Dark, Light and Night.
- 2 appearance modes: glass and plain.
- 3 surfaces for every language/theme/appearance combination: 1360×900 workspace, 1024×768 workspace and splash.

The capture validator must confirm the complete matrix, unique filenames, exact workspace dimensions, PNG readability and SHA-256 consistency. A local bilingual HTML gallery accompanies the images. These offscreen screenshots support visual review but do not replace native Windows DPI, display scaling or usability acceptance.

## Release gates — all mandatory

1. Exact-source full regression on Windows and Ubuntu, with no unexplained failures, errors or skips.
2. Fresh exact-source 36-image capture, integrity validation and human visual review.
3. Fresh portable and Setup builds; complete binary inventory, dependency provenance, license notices, checksums and manifest validation.
4. Offline portable and installed smoke tests, including install, first launch and uninstall on clean and pre-equipped Windows systems.
5. Qt/PySide6 LGPL and GPL module review, corresponding-source/notice obligations and aligned patched Python/Qt/OpenSSL runtime review.
6. Installer signing, native bilingual acceptance and owner approval before any public release.

A successful build, a passing subset of tests, a draft PR or an internal artifact is not a public release. Keep Stable and the forward Beta independent; selectively promote only verified features. No fixed Stable release date is promised.
