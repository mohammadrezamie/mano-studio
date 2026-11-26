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
| **Stable** | [Release plan #4](https://github.com/mohammadrezamie/mano-studio/issues/4) | [v1.0.0 candidate #24](https://github.com/mohammadrezamie/mano-studio/pull/24): [Windows installer and smoke](https://github.com/mohammadrezamie/mano-studio/actions/runs/45798904733) passed; [full regression](https://github.com/mohammadrezamie/mano-studio/actions/runs/45798904930), native acceptance and [redistribution #26](https://github.com/mohammadrezamie/mano-studio/pull/26) remain open; [isolated pinned build](https://github.com/mohammadrezamie/mano-studio/actions/runs/45804344694) queued; [binary security review](docs/STABLE_BINARY_SECURITY_REVIEW.md) identifies an obsolete TLS dependency requiring remediation. |
| **Beta** | [Development plan #23](https://github.com/mohammadrezamie/mano-studio/issues/23) | [develop/next-beta](https://github.com/mohammadrezamie/mano-studio/tree/develop/next-beta): new features and textbook coverage; [typography #25](https://github.com/mohammadrezamie/mano-studio/pull/25) and [visual QA #27](https://github.com/mohammadrezamie/mano-studio/pull/27) await integrated acceptance; offline paired screenshot gallery and five saved CPU programs added (14 local sample tests passed). |

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

## Permanent owner requirement — easy standalone installation (2026-11-26)
Both Stable and Beta require a one-step offline Windows Setup, no manual Python/Qt/pip or other prerequisite installation, no reinstall of compatible shared prerequisites, and no global PATH changes or destructive upgrades. Private bundled libraries are intentional for isolation. See docs/STANDALONE_INSTALLATION.md. This is a mandatory release gate (#4/#23/#10), not a completed native acceptance claim. #26 commit 3180a91c6d92e96e6648fe991cd9f10e7b49ea60 adds sanitized installed-process PATH, loaded private Python/Qt/SSL DLL checks and actual SSL version report; 3 local path tests passed in 0.04s with exact blobs e8fe55b4827bc00fef9493861d6ee8ba1d6ad567 and 2fa08d4579a9a0f0ee71402e40e94828c65c34be. Windows diagnostic and clean/pre-equipped VM tests pending. #25 and #27 reconciled without deleting changes, verified mergeable at ec309ca1842855c5b2fd62690f867166e1902722 and 9e805a5c52f488c81a5ae4a10d5e541f77997236. No product PR merged or release published.

## Stable and Beta checkpoint — 2026-11-26
- Stable exact #24 3ed419e3a37d9e233a4a908c08f9eccbbe80bf83 Ubuntu regression job 139836644367 on run 45798904930 completed success; actual log **1416 passed in 3631.56s**. JUnit artifact 15109449408, desktop previews 15111445195. Windows job 139836644580 still in progress. This is the original v1 candidate, not newer redistribution branch.
- #26 one-step installation diagnostic run 45807632417 (exact 3180a91c) passed Python 3.14.10 setup, isolated venv, pinned dependency installation, pip provenance validation and pip check; targeted tooling failed 1 case, 32 passed. Actual Windows failure: pathlib Path sort is case-insensitive on Windows; test_prune_only_targets expected uppercase Qt DLL before lowercase plugins directory. Fix explicitly sorts by relative POSIX path string, retaining same removal and dependency checks. Local 12 combined prune/redistribution tests passed (0.05s); verified exact Git blob 9e372af0e79792459261b977425d8e254c0a1c67. Corrective source 0fa786aa55266bdded0e30eacfcc70e24e279eaa. No new build artifact, native probe, TLS fix or legal approval from failed run. New candidate run pending visibility. Do not modify original #24/#22.
- Beta exact e9a4bc3f79e84c701c9140588a184fc3ac59fc89 (11 files) adds native CPU session checkpoints: source, all 4096 words via sparse nonzero memory, registers, flags, instruction count, breakpoints. Complete instruction boundaries only. Restore is validated state (not proof of execution history), never auto-runs, and begins new reverse history. New bilingual Computer Session menu and Workspace routing. 24 local actual CPU and persistence tests passed (0.10s); exact code/test/native envelope blobs 30dc47c205f2470df601463268adf15d74e58411, 57ec81c00729471eff4ccb1a1f711d491ea7b0bd, f7d5f92589700f5c89deceeec1deaaacd88bc257. Existing exact assembler, CPU, ISA, control and arithmetic modules reused. Two Qt locale tests authored, unexecuted locally. CPU close guard and partial-instruction/full trace persistence remain future work.
- #25 reconciled with current Beta by applying exact three typography additions to current workspace, preserving new CPU route; head 0bec2722579adf70acdd37b61547651bd5cab235. #27 all ten evidence changes preserved, head c38547dda73902adac46635eadc7bdedece629e7. Both branches retain prior history, no force or new PR; fresh visual tests needed.
- Permanent one-step install policy remains mandatory for both channels. No manual dependency install, shared-compatible prerequisite reinstall, global PATH change or automatic startup traffic; private packaged runtime intentionally isolated. Clean/pre-equipped Windows verification pending.

2026-11-26 continuation: fallback #22 exact full regression now successful on both platforms (1,376 each). Actual downloaded JUnit ZIPs independently compared, all identities match, no failures/errors/skips. See [regression evidence](docs/REGRESSION_EVIDENCE.md) and measured Workspace bottleneck. #24 Windows full regression remains running; #26 corrected installer run 45809656420 queued at inspection. No release approval. Beta 6fcd55ca adds CPU close/reset guard and draft save, 8 pure guard tests passed, native Qt cases pending. #25/#27 reconciled with Beta, fresh visual acceptance pending. Install policy remains unchanged.
