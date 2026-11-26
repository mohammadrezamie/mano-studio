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
  <img alt="Release status" src="https://img.shields.io/badge/release-candidate%20testing-E5A344">
  <a href="LICENSE"><img alt="MIT license" src="https://img.shields.io/badge/license-MIT-287D65"></a>
</p>

<p align="center">
  <a href="#quick-start">Quick start</a> · <a href="#academic-assignment">Academic core</a> · <a href="#visual-preview">Visual preview</a> · <a href="#development-status">Status</a> · <a href="#documentation">Docs</a>
</p>

## What you can do

| Workspace | Explore |
| --- | --- |
| **RTL editor** | Translate RTL to assembly using typing, an on-screen symbol pad, or a guided builder; export plain text. |
| **Computer** | Assemble programs, step through the Basic Computer, inspect registers and memory, reverse execution, explore arithmetic, microprogramming, pipelines and I/O. |
| **Digital Logic** | Edit circuits, inspect truth tables and Boolean equations, study sequential components, Karnaugh maps, FSM synthesis/reduction and memory. |
| **Learning Center** | Search bilingual interactive exercises across all 13 indexed chapters; keep local practice progress. |

Designed for English and Persian, with persistent language preferences, Light/Dark/Night themes and optional glass effects and motion. Core features work offline; only an explicit update check may contact GitHub.

## Development status — two permanent channels

| Channel | Plan | Current work |
| --- | --- | --- |
| **Stable** | [Release plan #4](https://github.com/mohammadrezamie/mano-studio/issues/4) | [v1.0.0 candidate #24](https://github.com/mohammadrezamie/mano-studio/pull/24): [Windows installer and smoke](https://github.com/mohammadrezamie/mano-studio/actions/runs/45798904733) passed; [full regression](https://github.com/mohammadrezamie/mano-studio/actions/runs/45798904930), native acceptance and [redistribution #26](https://github.com/mohammadrezamie/mano-studio/pull/26) remain open; [isolated pinned build](https://github.com/mohammadrezamie/mano-studio/actions/runs/45804344694) queued. |
| **Beta** | [Development plan #23](https://github.com/mohammadrezamie/mano-studio/issues/23) | [develop/next-beta](https://github.com/mohammadrezamie/mano-studio/tree/develop/next-beta): new features and textbook coverage; [typography #25](https://github.com/mohammadrezamie/mano-studio/pull/25) and [visual QA #27](https://github.com/mohammadrezamie/mano-studio/pull/27) await integrated acceptance; offline paired screenshot gallery added. |

The latest verified source baseline on main remains PR #15 (1,200 tests per OS in [run 45557009008](https://github.com/mohammadrezamie/mano-studio/actions/runs/45557009008); partial coverage across 13 chapters). The older [#22](https://github.com/mohammadrezamie/mano-studio/pull/22) build is a retained fallback, not the latest Beta feature channel. Its [Ubuntu regression](https://github.com/mohammadrezamie/mano-studio/actions/runs/45786384171) passed 1,376 tests; Windows remains pending.

**No accepted public release is confirmed.** Internal artifacts are not public Stable or Beta releases. Instructor delivery targets Monday 2026-11-30, subject to evidence. See [two-channel policy](docs/DEVELOPMENT_CHANNELS.md), [release acceptance evidence](docs/RELEASE_ACCEPTANCE_CHECKPOINT.md), [Actions](https://github.com/mohammadrezamie/mano-studio/actions) and [Releases](https://github.com/mohammadrezamie/mano-studio/releases). Snapshot 2026-11-26.

## Visual preview

The M-chip above is the approved **candidate** identity, exported from the vector geometry in the release candidate (not the older main application icon). Actual desktop captures are available from [the verified PR #15 CI run](https://github.com/mohammadrezamie/mano-studio/actions/runs/45557009008) under its artifacts. The Windows archive contains real English/Persian Qt previews in multiple themes; offscreen capture is not native Windows visual acceptance. GitHub sign-in may be required to download artifacts.

The internal v1 candidate also has [actual instructor-focused Qt captures](https://github.com/mohammadrezamie/mano-studio/actions/runs/45798904733) (artifact `ManoStudio-v1-instructor-preview`); the capture job passed, but native visual acceptance remains separate.

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
| [Release policy](docs/RELEASE_POLICY.md) | [Curriculum coverage](docs/CURRICULUM_COVERAGE.md) |
| [Documentation policy](docs/DOCUMENTATION_POLICY.md) | [Exercises](docs/EXERCISES.md) |

## Two tracks, one project

Stable maintains the latest accepted release; Beta develops the newest features continuously. Both advance independently, with selective verified promotion from Beta to Stable and relevant fixes back to Beta. See the [two-channel policy](docs/DEVELOPMENT_CHANNELS.md). Full textbook coverage is a goal, not a completion claim.

**Contributors and agents:** read [AGENTS.md](AGENTS.md) and [CONTINUE.md](docs/CONTINUE.md). Update README and affected documentation in the same work cycle as every meaningful project change. Record actual evidence, not anticipated results.

## Acknowledgments & license

An independent educational project for the computer architecture course, based on M. Morris Mano's *Computer System Architecture*. Academic acknowledgment and institutional details are subject to verification; no official endorsement is implied.

Released under the [MIT License](LICENSE). See [references](docs/REFERENCES.md) for technical sources.
