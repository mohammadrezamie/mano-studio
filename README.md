<p align="center">
  <img src="docs/assets/mano-studio.svg" alt="Mano Studio M-chip logo" width="112">
</p>

<h1 align="center">Mano Studio</h1>
<p align="center"><strong>Build. Translate. Simulate. Learn.</strong></p>
<p align="center">An offline-first desktop IDE for Morris Mano's Computer System Architecture.<br>From register-transfer notation to interactive computer architecture experiments.</p>

<p align="center">
  <a href="https://github.com/mohammadrezamie/mano-studio/actions"><img alt="Tests" src="https://github.com/mohammadrezamie/mano-studio/actions/workflows/tests.yml/badge.svg?branch=main"></a>
  <img alt="Python" src="https://img.shields.io/badge/Python-3.12-3776AB?logo=python&amp;logoColor=white">
  <img alt="Qt for Python" src="https://img.shields.io/badge/PySide6-Qt-41CD52?logo=qt&amp;logoColor=white">
  <img alt="Languages" src="https://img.shields.io/badge/UI-English%20%2F%20Persian-7664D8">
  <img alt="Release status" src="https://img.shields.io/badge/release-preparing%20beta-E5A344">
  <a href="LICENSE"><img alt="MIT license" src="https://img.shields.io/badge/license-MIT-287D65"></a>
</p>

<p align="center">
  <a href="#quick-start">Quick start</a> · <a href="#academic-assignment">Academic core</a> · <a href="#visual-preview">Visual preview</a> · <a href="#development-status">Status</a> · <a href="#documentation">Docs</a>
</p>

**You are viewing the next-generation branch.** Its MSI cache-coherence lesson is implemented in source, with 44 learning entries; GUI execution and visual evidence are pending. See [the MSI lesson](docs/CACHE_COHERENCE.md). The new [Omega interconnection model](docs/OMEGA_NETWORK.md) supports 2–64 ports, with 19 local regression tests passed; its bilingual interactive UI and catalog route are implemented; Qt execution is pending. The existing Karnaugh lab now supports [NAND-only and NOR-only synthesis](docs/UNIVERSAL_GATES.md) with a full truth-table equivalence guard; integrated tests remain pending. The [Boolean analysis lesson](docs/BOOLEAN_ANALYSIS.md) adds canonical SOP/POS, static hazard detection and a consensus repair preview (8 local pure-engine tests passed). The [Boolean laws inspector](docs/BOOLEAN_LAWS.md) evaluates 12 identity families and their dual forms (27 local tests passed); Qt verification remains pending. The [flip-flop reference tables](docs/FLIPFLOP_REFERENCE.md) derive characteristic and excitation rows directly from the clocked engine (11 local tests passed); Qt verification remains pending. The [setup/hold exercise](docs/TIMING_CONSTRAINTS.md) adds ideal timing constraints, waveform and violation inspection (11 local tests passed); GUI execution pending. The [storage-elements lesson](docs/STORAGE_ELEMENTS.md) adds SR NOR/NAND, D latch and abstract asynchronous D controls (12 local tests passed); GUI execution pending. The [carry look-ahead preset](docs/CARRY_LOOKAHEAD.md) adds a structural 4-bit alternative to ripple carry (10 local generator tests passed; integration pending). The [Shannon MUX realization](docs/MUX_SYNTHESIS.md) builds editable circuits from the selected Karnaugh completion (9 local generator tests passed; integration verification pending). The [practical laboratory policy](docs/PRACTICAL_LAB_POLICY.md) requires useful experiments and saved samples across the book. The [circuit library](docs/CIRCUIT_LIBRARY.md) adds six editable classic samples, chapter grouping and reusable saved-file block insertion (14 local file/planner tests, 76 independently checked sample truth rows over two checkpoints; integrated GUI pending). First beta Windows installer and portable CI artifacts were successfully built and smoke-tested in run [45786384159](https://github.com/mohammadrezamie/mano-studio/actions/runs/45786384159); full final regression and public release remain pending. The [shared RAM/register bus lab](docs/DATABUS_LAB.md) combines existing register, memory and tri-state engines with three saved stepwise experiments (18 exact local tests passed, 1,280 transfer combinations; Qt pending). The [native .mano format and update download](docs/NATIVE_FILES_AND_UPDATES.md) add native RTL/ASM/circuit files, optional Windows association and consent-based digest-checked official installer downloads (29 local pure tests; Windows/Qt/live release pending). Native [bus experiment checkpoints](docs/DATABUS_LAB.md) now restore RAM, registers, staged controls and the last 64 transfer events (44 local tests passed; Qt pending). Native Karnaugh/FSM designs and three saved examples now use .mano (32 local tests passed; Qt pending). See the [permanent owner backlog](docs/OWNER_BACKLOG.md) and [issue #23](https://github.com/mohammadrezamie/mano-studio/issues/23). Native FSM runtime sessions now preserve current state, selected input and the last 64 clock events (61 local tests including 29 new session cases; Qt pending). The shared RAM/register bus now connects the real 4-bit ALU with 16 operations and two additional saved scenarios (68 local tests including 8192 operation/input combinations; Qt pending). Update downloads now support progress, cooperative cancel and elapsed-time checks (24 local tests; real Release/Qt pending). A focused next-beta CI gate is separate from first-beta verification. This is not the first beta release candidate.

## What you can do

| Workspace | Explore |
| --- | --- |
| **RTL editor** | Translate RTL to assembly using typing, an on-screen symbol pad, or a guided builder; export plain text. |
| **Computer** | Assemble programs, step through the Basic Computer, inspect registers and memory, reverse execution, explore arithmetic, microprogramming, pipelines and I/O. |
| **Digital Logic** | Edit circuits, inspect truth tables and Boolean equations, study sequential components, Karnaugh maps (including NAND/NOR-only build on next-beta), FSM synthesis/reduction and memory. |
| **Learning Center** | Search bilingual interactive exercises across all 13 indexed chapters; keep local practice progress. |

Designed for English and Persian, with persistent language preferences, Light/Dark/Night themes and optional glass effects and motion. Core features work offline; only an explicit update check may contact GitHub.

## Development status

| Track | Current milestone |
| --- | --- |
| **Main — verified source baseline** | PR [#15](https://github.com/mohammadrezamie/mano-studio/pull/15) merged; 1,200 tests passed on each OS in [run 45557009008](https://github.com/mohammadrezamie/mano-studio/actions/runs/45557009008). 42 learning entries across 13 chapters (partial coverage). |
| **Release — Windows x64 beta** | [PR #22](https://github.com/mohammadrezamie/mano-studio/pull/22), v0.3.0-beta.1 candidate; final tests and independent installer build queued, native acceptance and publication pending. |
| **Next generation** | [develop/next-beta](https://github.com/mohammadrezamie/mano-studio/tree/develop/next-beta): MSI and Omega add the 43rd and 44th entries; Omega routing model (19 previously recorded local tests passed), bilingual canvas and exercises implemented. Full Qt evidence pending. |

**No downloadable public release has been verified or published.** Development artifacts are not stable releases. Follow [release issue #4](https://github.com/mohammadrezamie/mano-studio/issues/4), [curriculum issue #13](https://github.com/mohammadrezamie/mano-studio/issues/13), [Actions](https://github.com/mohammadrezamie/mano-studio/actions) and [Releases](https://github.com/mohammadrezamie/mano-studio/releases) for live state. This snapshot is dated 2026-11-25; evidence refers to the named commits/runs, not every later change.

## Visual preview

The M-chip above is the approved **candidate** identity, exported from the vector geometry in the release candidate (not the older main application icon). Actual desktop captures are available from [the verified PR #15 CI run](https://github.com/mohammadrezamie/mano-studio/actions/runs/45557009008) under its artifacts. The Windows archive contains real English/Persian Qt previews in multiple themes; offscreen capture is not native Windows visual acceptance. GitHub sign-in may be required to download artifacts.

See [design system](docs/DESIGN_SYSTEM.md), [brand system](docs/BRAND_SYSTEM.md) and [animation guide](docs/ANIMATION_GUIDE.md). Keep screenshots few, representative, genuine and clearly dated; never substitute generated concepts for running software.

## Quick start

For a source preview (Python 3.12 is the CI-tested version):

```sh
git clone https://github.com/mohammadrezamie/mano-studio.git
cd mano-studio
python -m venv .venv
```

Activate the environment on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Then install and launch:

```sh
python -m pip install -r requirements.txt
python main.py
```

Choose a language, enter RTL, translate, and export assembly. Press **Ctrl+K** to open the Learning Center. For regression tests, install `requirements-dev.txt` and run `python -m pytest -q`. Windows installation packages will be listed under Releases only after verification; do not treat a CI archive as an accepted installer.

## Academic assignment

**[rtl_translator.py](rtl_translator.py) is the single standalone source file for instructor review.** It uses only the Python standard library, includes translation and validation, and supports all 25 named Basic Computer instructions in the documented provisional dialect. Optional simulation and UI are separate.

```sh
python rtl_translator.py examples/add.rtl -o result.asm
```

[Translator defense guide](docs/TRANSLATOR.md) · [Supported RTL dialect](docs/RTL.md) · [Example input](examples/add.rtl)

برای دفاع، فقط فایل `rtl_translator.py` را باز کنید؛ امکانات جانبی برنامه از هسته تکلیف مستقل هستند.

## Architecture

```text
RTL text / guided builder
          │
          ▼
  rtl_translator.py ──► Assembly text
          ▲
          │
      PySide6 UI
          │
          ├── Computer: assembler + simulator + architecture models
          ├── Digital Logic: circuits + mathematical models
          └── Learning Center: bilingual catalog + existing tool routes
```

The academic translator remains dependency-free and independently testable. See [technology decisions](docs/TECH_STACK.md) and [maintenance plan](docs/MAINTAINABILITY.md).

## Documentation

| Start here | Technical guides |
| --- | --- |
| [Project specification](docs/PROJECT.md) | [RTL dialect](docs/RTL.md) |
| [Current status](docs/STATUS.md) | [Computer simulator](docs/SIMULATOR.md) |
| [Continuation checkpoint](docs/CONTINUE.md) | [Logic Lab](docs/LOGIC_LAB.md) |
| [Roadmap](docs/ROADMAP.md) | [Learning Center](docs/LEARNING_CENTER.md) |
| [Release policy](docs/RELEASE_POLICY.md) | [Curriculum coverage](docs/CURRICULUM_COVERAGE.md) · [Detailed topic audit](docs/TEXTBOOK_AUDIT.md) |
| [Documentation policy](docs/DOCUMENTATION_POLICY.md) | [Exercises](docs/EXERCISES.md) |

## Two tracks, one project

The release track stabilizes a Windows-first beta without scope creep. The next-generation track expands the textbook models, visual tools and educational experiments independently. Neither track waits for the other to finish. Full textbook coverage is a goal, not a completion claim. New libraries are welcome when licensing, offline operation, packaging and maintainability are compatible.

**Contributors and agents:** read [AGENTS.md](AGENTS.md) and [CONTINUE.md](docs/CONTINUE.md). Update README and affected documentation in the same work cycle as every meaningful project change. Record actual evidence, not anticipated results.

## Acknowledgments & license

An independent educational project for the computer architecture course, based on M. Morris Mano's *Computer System Architecture*. Academic acknowledgment and institutional details are subject to verification; no official endorsement is implied.

Released under the [MIT License](LICENSE). See [references](docs/REFERENCES.md) for technical sources.


## First stable instructor delivery target
Monday 2026-11-30: see [v1.0 delivery plan](docs/V1_DELIVERY_PLAN.md) and [issue #4](https://github.com/mohammadrezamie/mano-studio/issues/4). The verified installable beta remains separate from the conditional stable target and ongoing next-generation scope. Reproducible source counts: `python source_metrics.py HEAD`.


Visual-first instructor presentation and exact standalone source access are shared with the independent [v1 candidate PR #24](https://github.com/mohammadrezamie/mano-studio/pull/24). See [acceptance criteria](docs/V1_INSTRUCTOR_ACCEPTANCE.md). The next-generation version and native file dispatch remain independent.

Beta feature increment: the Computer workspace offers five native saved assembly examples (addition, counted loop, subroutine, indirect addressing and carry). All 14 local file/catalog and actual CPU result tests passed; Qt integration evidence remains pending. See [Simulator](docs/SIMULATOR.md) and [Beta plan #23](https://github.com/mohammadrezamie/mano-studio/issues/23).

## FSM unsaved session protection — 2026-11-26
Beta #23/#11: state design + base state + bounded clock inputs + staged input tracked against the last loaded/saved checkpoint, without re-minimization for dirty checks. Logic Lab close checks FSM even when another tab is active; Save uses a native-only .mano dialog, Cancel or failed save prevents close, Discard permits close without mutating the saved baseline. Legacy design-only export never clears unsaved runtime history. Native session open/save establishes clean baseline; design-only open resets staged input to zero. Explicit replacement confirmation retained. Six local pure tests passed (0.03s), exact tested blobs session_guard.py 9bce6c2547aedc14c0473635c3426282298a8d0a, tests/test_session_guard.py e3c31f6d62962c866fcee3bfd34cbf59dc9116bb. Two bilingual Qt close tests authored, existing state-only test cleanup made explicit; Qt not run locally. Protection is for close/explicit file replacement, not undo of every table edit or CPU runtime persistence. No Stable changes or new issue/PR.

## Native CPU checkpoints — 2026-11-26
Beta #3/#23: new .mano kind cpu-run, saves source, entire 4096-word memory (sparse nonzero representation), width-validated registers and flags, instruction count and breakpoints at complete instruction boundaries. Restore validates and assembles source before replacement, preserves zeroed/self-modified memory, does not execute automatically, and restarts reversible trace at checkpoint. Snapshot is state, not proof of prior execution. New bilingual Computer Session menu and Workspace .mano routing; wrong extension, invalid session and partial instruction save rejected. 24 actual local tests passed (0.10s), including exact continuation and atomic rejection; exact tested source blobs cpu_session.py 30dc47c205f2470df601463268adf15d74e58411, test 57ec81c00729471eff4ccb1a1f711d491ea7b0bd, mano_file f7d5f92589700f5c89deceeec1deaaacd88bc257. Existing assembler/CPU dependencies matched previous verified Git hashes. Two locale Qt cases authored, not run locally (PySide6 absent). Full historical reverse trace, partial instruction serialization, CPU unsaved close protection and native file association acceptance remain open. No Stable changes.

Beta visual polish proposes safer memory editing: explicit table selection synchronizes the address field; automatic refresh preserves typed addresses. Both-locale regression cases added, Windows QA pending.

Instructor visual QA: exact 48-view bilingual capture coverage and a local review gallery are now integrated with pull-request Windows CI, including compact-layout and memory-inspector regressions. Native visual acceptance remains a separate required gate. See [instructor acceptance](docs/V1_INSTRUCTOR_ACCEPTANCE.md).


The 48-view QA work is maintained in rebased [PR #29](https://github.com/mohammadrezamie/mano-studio/pull/29); stale-base PR #27 is closed. Exact-head Windows visual CI is enabled; capture and native visual review remain pending.
