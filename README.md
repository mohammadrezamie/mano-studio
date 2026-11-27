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
  <img alt="Release status" src="https://img.shields.io/badge/release-in%20review-E5A344">
  <a href="LICENSE"><img alt="MIT license" src="https://img.shields.io/badge/license-MIT-287D65"></a>
</p>

<p align="center">
  <a href="#download">Download</a> · <a href="#quick-start">Quick start</a> · <a href="#academic-assignment">Academic core</a> · <a href="#visual-preview">Visual preview</a> · <a href="#development-status">Status</a> · <a href="#documentation">Docs</a>
</p>

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
| Stable | [PR #24](https://github.com/mohammadrezamie/mano-studio/pull/24), 1.0.0 candidate. [1,561 tests per OS](https://github.com/mohammadrezamie/mano-studio/actions/runs/45961164536); [installer](https://github.com/mohammadrezamie/mano-studio/actions/runs/45961164498) passed; verified private release draft created. |
| Beta | [PR #37](https://github.com/mohammadrezamie/mano-studio/pull/37), 1.1.0-beta.1 candidate. [Installer](https://github.com/mohammadrezamie/mano-studio/actions/runs/46000977621) passed; [parallel final gate](https://github.com/mohammadrezamie/mano-studio/actions/runs/46000977462) passed all 12 jobs; 2,265 tests per OS, zero skips. |
| Next generation | [develop/next-beta](https://github.com/mohammadrezamie/mano-studio/tree/develop/next-beta), independent feature development. |

Public release remains subject to actual applicable security review, redistribution/source obligations, native Windows acceptance and authenticity review. Follow [Stable #4](https://github.com/mohammadrezamie/mano-studio/issues/4), [Beta #23](https://github.com/mohammadrezamie/mano-studio/issues/23), and [Releases](https://github.com/mohammadrezamie/mano-studio/releases) for current evidence (checkpoint 2026-11-27). No claim of a bug-free application.

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

Choose a language, enter RTL, translate, and export assembly. Press **Ctrl+K** to open the Learning Center. For regression tests, install `requirements-dev.txt` and run `python -m pytest -q`. See [Download](#download) for the Windows Setup and Portable options, device compatibility and review-build status.

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

The Stable release track stabilizes the Windows-first app without scope creep; the forward Beta line remains independently versioned. The next-generation track expands the textbook models, visual tools and educational experiments independently. Neither track waits for the other to finish. Full textbook coverage is a goal, not a completion claim. New libraries are welcome when licensing, offline operation, packaging and maintainability are compatible.

**Contributors and agents:** read [AGENTS.md](AGENTS.md) and [CONTINUE.md](docs/CONTINUE.md). Update README and affected documentation in the same work cycle as every meaningful project change. Record actual evidence, not anticipated results.

## Acknowledgments & license

An independent educational project for the computer architecture course, based on M. Morris Mano's *Computer System Architecture*. Academic acknowledgment and institutional details are subject to verification; no official endorsement is implied.

Released under the [MIT License](LICENSE). See [references](docs/REFERENCES.md) for technical sources.

## Download

<p align="center">
  <a href="https://github.com/mohammadrezamie/mano-studio/releases"><img alt="Download Windows Setup — official release page" src="https://img.shields.io/badge/Download-Windows%20x64%20Setup-2563eb?style=for-the-badge&amp;logo=windows&amp;logoColor=white"></a>
  <a href="https://github.com/mohammadrezamie/mano-studio/releases"><img alt="Portable ZIP — official release page" src="https://img.shields.io/badge/Download-Portable%20ZIP-475569?style=for-the-badge"></a>
</p>

**Publication status:** the initial releases are still under acceptance review. The buttons above open the official Releases page; there is no public installer download there yet. Do not redistribute review builds or treat them as accepted releases.

| Version | Device / OS | Architecture | Setup (install) | Portable (no install) | Status |
| --- | --- | --- | --- | --- | --- |
| **1.0.0 — Stable** | Windows desktop / laptop, 10 / 11 target | Intel / AMD x64 | [Setup · 35.0 MB (review)](https://github.com/mohammadrezamie/mano-studio/actions/runs/45961164498/artifacts/15180752782) | [ZIP · 51.0 MB (review)](https://github.com/mohammadrezamie/mano-studio/actions/runs/45961164498/artifacts/15180064025) | 1,561 tests per OS passed; private draft |
| **1.1.0-beta.1 — Beta** | Windows desktop / laptop, 10 / 11 target | Intel / AMD x64 | [Setup · 36.8 MB (review)](https://github.com/mohammadrezamie/mano-studio/actions/runs/46000977621/artifacts/15197803727) | [ZIP · 53.6 MB (review)](https://github.com/mohammadrezamie/mano-studio/actions/runs/46000977621/artifacts/15198955230) | 2,265 tests per OS passed; publication review |
| — | Windows 32-bit | x86 | Not available | Not available | [Feasibility #54](https://github.com/mohammadrezamie/mano-studio/issues/54) |
| — | Windows on ARM | ARM64 | Not available | Not available | [Feasibility #54](https://github.com/mohammadrezamie/mano-studio/issues/54) |
| — | Linux / macOS | — | Not available | Not available | Source only; no released package |

GitHub Actions artifacts are temporary review files (GitHub sign-in may be required), not public releases. The official Releases page is the permanent download location; once a release is published, choose its Setup EXE for installation or its portable ZIP to run without installing. Verify the accompanying SHA-256 checksum. These candidates are not Authenticode-signed.

### Device and system compatibility

| Device / operating system | Support for this build |
| --- | --- |
| Windows 11, Intel/AMD **64-bit (x64)** desktop or laptop | Target platform; automated Windows packaging/smoke verified, native acceptance pending |
| Windows 10, Intel/AMD **64-bit (x64)** | Qt 6.12 supports Windows 10 1809+; exact native OS acceptance is pending; use a security-supported Windows edition |
| Windows **32-bit (x86)** | No desktop installer; current Qt/PySide6 dependencies do not ship Windows x86 wheels |
| Windows on ARM (ARM64) | No native package or verified emulation support yet |
| Linux / macOS | Source development possible on compatible dependencies; no official installer or macOS native acceptance |
| iPhone / iPad / Android | Not supported by this desktop release |

The Windows Setup bundles its application-private Python/Qt runtime; no separate Python, pip or Qt installation is needed. After installation, core tools work offline. On Windows, open **Settings → System → About → System type** to identify x64, x86 or ARM64 before downloading.

The standalone [RTL translator](rtl_translator.py) uses only the Python standard library and can be run with a compatible 32-bit Python installation, but that is not the full desktop app. A future 32-bit desktop build requires a supported GUI dependency strategy and independent installation and regression evidence. See [Qt supported platforms](https://doc.qt.io/qt-6/supported-platforms.html) and [PySide6 distribution files](https://pypi.org/project/PySide6/6.12.0/#files).

**راهنمای دانلود:** نسخه فعلی برای رایانه و لپ‌تاپ ویندوز ۶۴ بیتی (Intel/AMD) ساخته شده است. برای نصب عادی، Setup و برای اجرای بدون نصب، Portable را انتخاب کنید. فعلاً فایل‌ها آزمایشی‌اند و انتشار عمومی نهایی نشده است. نسخه کامل ویندوز ۳۲ بیتی و ARM64 هنوز تأیید نشده است.
