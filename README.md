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

**This branch tracks the Stable 1.0.0 internal candidate (PR #24 and redistribution PR #26); it is not a public release.** The latest Stable source now removes the in-app translator viewer and switches instructor evidence to a validated 36-image bilingual matrix. Fresh exact-head Windows/Ubuntu tests and a Windows candidate installer are being rerun; check the [PR checks](https://github.com/mohammadrezamie/mano-studio/pull/26/checks) for live state. Earlier artifacts belong to older source revisions and do not validate this update. Security, LGPL/source, clean-machine, native bilingual and signing gates remain open. The separate forward Beta is 1.1.0-dev.1 in PR #36 and remains ahead of Stable.

## What you can do

| Workspace | Explore |
| --- | --- |
| **RTL editor** | Translate RTL to assembly using typing, an on-screen symbol pad, or a guided builder; export plain text. |
| **Computer** | Assemble programs, step through the Basic Computer, inspect registers and memory, reverse execution, explore arithmetic, microprogramming, pipelines and I/O. |
| **Digital Logic** | Edit circuits, inspect truth tables and Boolean equations, study sequential components, Karnaugh maps, FSM synthesis/reduction and memory. |
| **Learning Center** | Search bilingual interactive exercises across all 13 indexed chapters; keep local practice progress. |

Designed for English and Persian, with persistent language preferences, Light/Dark/Night themes and optional glass effects and motion. Core features work offline; only an explicit update check may contact GitHub.

## Development status

| Track | Current milestone |
| --- | --- |
| **Stable — v1.0.0** | [PR #24](https://github.com/mohammadrezamie/mano-studio/pull/24) and [redistribution PR #26](https://github.com/mohammadrezamie/mano-studio/pull/26). Exact-source regression and the Windows candidate installer are being rerun after the standalone-translator and 36-view evidence port; see [live PR checks](https://github.com/mohammadrezamie/mano-studio/pull/26/checks) and [Stable branch Actions](https://github.com/mohammadrezamie/mano-studio/actions?query=branch%3Aquality%2Fredistribution-gate). Older build/smoke artifacts are stale for this source. LGPL, OpenSSL/Qt security, native, clean-VM and signing review remain open.
| **Forward Beta — v1.1.0** | Draft [PR #36](https://github.com/mohammadrezamie/mano-studio/pull/36), current development version 1.1.0-dev.1, proposed first prerelease v1.1.0-beta.1. Current-head visual acceptance [45905561919](https://github.com/mohammadrezamie/mano-studio/actions/runs/45905561919) passed; exact-head combined integration [45905561920](https://github.com/mohammadrezamie/mano-studio/actions/runs/45905561920) is still running focused Qt regressions. |
| **Next generation** | [develop/next-beta](https://github.com/mohammadrezamie/mano-studio/tree/develop/next-beta) continues independently; advanced textbook coverage is not a blocker for the first two releases. |

**No downloadable public release has been verified or published.** The older [PR #22](https://github.com/mohammadrezamie/mano-studio/pull/22) v0.3.0-beta.1 is fallback-only and superseded by the forward 1.1.0 Beta line. Follow [release issue #4](https://github.com/mohammadrezamie/mano-studio/issues/4), [curriculum issue #13](https://github.com/mohammadrezamie/mano-studio/issues/13), [Actions](https://github.com/mohammadrezamie/mano-studio/actions) and [Releases](https://github.com/mohammadrezamie/mano-studio/releases) for live state. This snapshot is dated 2026-11-27; evidence refers to the named commits/runs, not every later change.

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

**[rtl_translator.py](rtl_translator.py) is the single standalone source file for instructor review.** It uses only the Python standard library, includes translation and validation, and supports all 25 named Basic Computer instructions in the documented provisional dialect. The desktop intentionally has no in-app source viewer or source editor: download this file separately for explanation and defense. Optional simulation and UI remain separate.

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

The release track stabilizes a Windows-first beta without scope creep. The next-generation track expands the textbook models, visual tools and educational experiments independently. Neither track waits for the other to finish. Full textbook coverage is a goal, not a completion claim. New libraries are welcome when licensing, offline operation, packaging and maintainability are compatible.

**Contributors and agents:** read [AGENTS.md](AGENTS.md) and [CONTINUE.md](docs/CONTINUE.md). Update README and affected documentation in the same work cycle as every meaningful project change. Record actual evidence, not anticipated results.

## Acknowledgments & license

An independent educational project for the computer architecture course, based on M. Morris Mano's *Computer System Architecture*. Academic acknowledgment and institutional details are subject to verification; no official endorsement is implied.

Released under the [MIT License](LICENSE). See [references](docs/REFERENCES.md) for technical sources.


## Instructor v1.0.0 candidate (not accepted stable)
This branch prepares the first stable delivery for Monday, 2026-11-30. Priority: standalone RTL-to-Assembly Python file, stability, and premium bilingual presentation. See [instructor acceptance](docs/V1_INSTRUCTOR_ACCEPTANCE.md). Candidate packaging and full tests remain required. Later-generation functionality is promoted only after validation; verified beta artifacts remain independent.

## Public redistribution preflight

The internal v1 Windows archive passed automated smoke and binary integrity checks, but public distribution remains blocked pending Qt license evidence and module review. See [the redistribution preflight](docs/REDISTRIBUTION_PREFLIGHT.md). No public release is approved by this audit.

## Maintained Python diagnostic and TLS evidence — 2026-11-26
Internal #26 Windows diagnostic switches only its own PR builds to Python 3.14.10 (official release 2026-10-25). Other frozen candidates retain existing runtime. This supersedes queued 3.12 diagnostic run 45804344694; branch-specific concurrency may cancel it. Python migration is not proven compatible or sufficient to fix OpenSSL. Official OpenSSL November 24 advisory CVE-2026-121482 lists 3.5.0 before 3.5.10 affected; use 3.5.10 as explicit dated review baseline, not an automatic release/security approval. New runtime_evidence.py scans actual portable ZIP for SSL/crypto DLL embedded versions and SHA-256 plus build interpreter ssl version. Reports flags and always requires manual review; string scan is heuristic, not PE import or loaded-runtime attestation. Seven local pytest fixtures passed (0.04s); local blobs 302f81d034e8222e2e244f56c80fbde73b346cf2 and e5f0a80c3b1bb5a84bdb9237354192c25c56995d. Actual old v1 archive produced four DLL rows, three flags: 3.0.16, 3.5.9 and known historical build SSL 3.0.16 (supplied from prior evidence, not measured in Linux). New Windows build pending, no approval. Sources: https://www.python.org/downloads/release/python-31410/ and https://openssl-library.org/news/vulnerabilities-3.5/ .

Owner requirement: [standalone Windows installation](docs/STANDALONE_INSTALLATION.md) is a permanent gate for both channels. Setup must not require separate Python/Qt/pip, reinstall compatible shared prerequisites or modify global PATH. App-private bundling is intentional. Clean and pre-equipped Windows acceptance remains pending.
