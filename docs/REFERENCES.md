# References and research leads
Primary: M. Morris Mano, Computer System Architecture, 3rd edition, Prentice Hall, 1993; chapters 4 Register Transfer and Microoperations, 5 Basic Computer Organization and Design, 6 Programming the Basic Computer. Exact instructor edition and input grammar pending.
Previously discussed comparison leads (not independently reverified in this handoff; inspect existence, license and functionality before reuse):
- https://github.com/TomerAberbach/mano-simulator — assembler/simulator
- https://github.com/MahdiBaghbani/Python-Basic-Computer-Assembler — Python assembler
- https://github.com/YashG2009/mano-16bit-sim-desktop — desktop simulator
- https://github.com/MohsenSafari83/Mano-Vision — visualization
Use as inspiration only; no copying without license review.
Technical docs: https://doc.qt.io/qtforpython-6/ ; https://pyinstaller.org/ ; https://jrsoftware.org/isinfo.php ; https://docs.github.com/en/rest/releases ; https://docs.github.com/en/actions
Academic profile leads: https://srb.iau.ir/ ; https://scholar.google.com/scholar?q=Siavash+Eshaghi . Not verified personal profiles. Product name is provisional branding, not trademark-cleared.

## UX research — 2026-11-24
- https://code.visualstudio.com/docs/editing/editingevolved — contextual Peek/navigation; adapt to source/output mapping without leaving the editor. https://code.visualstudio.com/docs/editing/getting-started/userinterface — progressive disclosure and editor-first layout.
- https://doc.qt.io/qtforpython-6/PySide6/QtWidgets/QComboBox.html and https://doc.qt.io/qtforpython-6/PySide6/QtWidgets/QCompleter.html — standard Qt selector/search APIs. Use existing Qt, no new dependencies.
- https://github.com/TomerAberbach/mano-simulator — verified README describes JavaFX assembler and simulator for Mano ch. 5, MIT license. Candidate for later independent behavior comparison; no source imported in this checkpoint.
- https://github.com/logisim-evolution/logisim-evolution — verified GPLv3, digital circuit editor/simulator. Workflow inspiration only; do not copy GPL code into MIT-only Mano Studio without a separate license decision.
Research decisions: consolidate builder and reference in one searchable panel, preserve three input modes and keyboard-free construction, link source and output using existing translator line metadata. Original implementation, no borrowed code/assets or new runtime dependency. Research is selective, not exhaustive.

## Read-only TakinTech research — 2026-11-24
Inspected TakinTech AGENTS.md, START_HERE, canonical documentation map, CI_BUDGET and discovered skills via GitHub read-only. Read canonical .agents/skills/ui-ux-pro-max/SKILL.md, frontend-design/SKILL.md, tna-theme-day-night/SKILL.md, tna-free-local-ci/SKILL.md, tna-e2e-browser-qa/SKILL.md, technical-debt/SKILL.md (relevant excerpts). Adopted general patterns: shared semantic colors, labeled controls, no decorative motion, exact-head CI evidence, explicit candidate build, source/owner boundaries. Laravel/web-specific implementation not applicable. No skill scripts executed, no code/assets copied, no TakinTech writes. No new dependencies.

## Chapter coverage and debugger design
- Morris Mano, Computer System Architecture, 3rd ed., chapters 3–4: fixed-width representation and arithmetic/logic/shift operations; chapter 5–6: Basic Computer and programming. https://studylib.net/doc/28115245/manuel-computer-system-architecture-by-morris-mano-- (chapter section indexing; independent original implementation, no text or figures imported).
- https://sourceware.org/gdb/current/onlinedocs/gdb.html/Process-Record-and-Replay.html — bounded execution log and reverse navigation inspiration; original StepEvent-based implementation, no source copied.

## Quality-first external research
- https://github.com/mortbopet/Ripes — visual processor/pipeline/cache teaching patterns; separate RISC-V architecture, no source imported.
- https://github.com/logisim-evolution/logisim-evolution — GPLv3 logic circuit workflow reference, not copied.
- https://github.com/zhiyiYo/PyQt-Fluent-Widgets — modern navigation and control hierarchy reference; license obligations require review before any reuse, not a dependency.
- https://doc.qt.io/qt-6/qlistwidget.html and https://doc.qt.io/qt-6/qstackedwidget.html — Qt-native controls for accessible page navigation. Implemented original rail over existing tab state, no third-party code or assets imported.
