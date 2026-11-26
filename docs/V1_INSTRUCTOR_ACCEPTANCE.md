# Instructor-ready v1 visual and academic acceptance

Owner direction 2026-11-26: the first stable release is targeted for Monday 2026-11-30. The assignment is RTL-to-Assembly, not complete textbook coverage. Presentation quality is an explicit acceptance criterion, alongside correctness and stability. Add features until the deadline only after independent verification and rechecking the exact integrated release candidate. Maintain independent next-generation development. No arbitrary package-size or library restriction; choose technology for actual UX, offline reliability, licensing and testability.

## Implemented candidate changes

- Derived from exact successful installable beta ecb6647c38a93a4eb9c2171c99c10392abd15e72, without changing PR #22 or its running tests.
- Current stack retained deliberately: Python 3.10+ standalone core, PySide6 / Qt desktop, original Qt-painted and SVG visual assets, PyInstaller and Inno Setup Windows x64 packaging. No rewrite or new dependency needed for this pass.
- Version 1.0.0 is an internal candidate until all release gates pass. Central version policy permits exactly 1.0.0 and existing 0.x prereleases; manifest still marks native acceptance and public release false. Version-specific updater and manifest tests updated, no relaxation of checksums, license or smoke gates.
- Layered workspace editor panels, clearer typographic hierarchy, version chip, reorganized brand header; the standalone translator remains a separate downloadable file and is not exposed through an in-app source viewer. Refined splash card with dedicated credits and startup-message footer. Three themes, glass/plain and reduced-motion options remain.
- The only academic converter source is the root-level standalone rtl_translator.py; the application calls its translate() API but provides no in-app source viewer, editor or export action. Download the file directly from the repository when preparing the instructor explanation.
- Dedicated instructor acceptance matrix captures actual Qt workspace at 1360×900 and 1024×768, splash for each of two locales × three themes × glass/plain (36 images expected). Verify the real screenshots for clipping, typography, contrast and presentation quality; offscreen screenshots do not establish native Windows usability.

## Evidence and outstanding gates

The standalone translator remains independently testable with Python standard library only; no source-viewer helper or GUI dependency is required. The actual CLI regression remains separate from the desktop UI tests; no modification to rtl_translator.py.

Qt and PowerShell unavailable locally. Candidate UI, splash, full versioned manifest tests and packaging have not yet executed. New focused GUI regression and screenshot capture required on Windows candidate installer workflow, plus full cross-platform regression, native installed demo, redistribution acceptance and verified release assets. Do not publish or label accepted stable before these gates. The independently built beta is a fallback. Next-beta improvements require tested, selective promotion; no blind merge.

## Rebased instructor screenshot evidence — 2026-11-26
The 36-capture QA work is rebased onto the latest visual-polish head after the native-document fix was merged into next-beta. It requires exactly all locale/theme/glass/workspace-size/splash combinations, enforces 1360×900 and 1024×768 workspace sizes, checks manifest hashes/dimensions and rejects duplicate, missing or stale PNGs. A bilingual local gallery is generated. Seven pure fixture tests passed previously (0.08s); the prior 36-image Qt set passed independent Pillow decoding and hash checks. Exact evidence source/test blobs d650ce3f8a67e2e66948d7b9f543b864ffe65641 / ccf5262bc12cca50fd10ab937bb2e1ed555af765; gallery blobs 5980a144084cd650f21e58b3f669bab8e56e0b57 / c8e896fed3f10d7bb9bdacd6c83e333f7bed14cc. Windows PR workflow covers evidence fixtures, typography, compact layout, academic translator isolation, memory inspector regressions and real Qt capture. Current rebased-head Qt execution is pending; image completeness is not native DPI, pixel-level visual or clean-machine acceptance. No academic translator or Stable candidate change.


## Owner clarification — no in-app source viewer (2026-11-27)
The earlier source-viewer action and dialog are removed. rtl_translator.py remains the one isolated, downloadable academic Python file at the repository root; the GUI delegates to its public translate() function and does not display or export its source. Instructor visual evidence therefore covers only the actual workspace at 1360×900 and 1024×768 plus splash, across both locales, three themes and glass/plain: 36 images. This supersedes the earlier 48-image matrix that included source-dialog screenshots.
