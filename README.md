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

**No accepted public release is confirmed.** Internal artifacts are not public Stable or Beta releases. Stable and optional Beta releases are independently quality-gated, with no mandatory version number or fixed date. See [two-channel policy](docs/DEVELOPMENT_CHANNELS.md), [release acceptance evidence](docs/RELEASE_ACCEPTANCE_CHECKPOINT.md), [Actions](https://github.com/mohammadrezamie/mano-studio/actions) and [Releases](https://github.com/mohammadrezamie/mano-studio/releases). Snapshot 2026-11-26.

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

## v1.0.0 full cross-platform regression — 2026-11-26
Original #24 exact source 3ed419e3a37d9e233a4a908c08f9eccbbe80bf83: run 45798904930 both jobs SUCCESS. Actual Windows job 139836644580: 1,416 passed in 8242.08s; Ubuntu job 139836644367: 1,416 passed in 3631.56s. Downloaded actual JUnit ZIPs 15119999661 (Windows) and 15109449408 (Ubuntu), both CRC valid; offline verifier confirmed exact same 1,416 unique identities, 0 failures/errors/skips on each platform. Machine-readable evidence docs/v1-regression-evidence.json records exact archive hashes and timing. Workspace share 99.69% Windows, 98.99% Ubuntu. This closes original #24 serial regression gate, not final redistributed candidate #26 (run 45809656420 queued at last inspection), native clean/pre-equipped PC acceptance, security or licensing gates. No public release. Beta 5d2309d48ef3ce4cf311c76f36b984d29abce427 supports reopening native assembly drafts; 10 local tests passed, Qt pending. #25/#27 reconciled with visual heads 54b713f001b6d766a962464907617898adde8456 and 3785db565e2eb709a6a9708b5d34d45b22adfe39; both mergeable.

## Verified Windows standalone rebuild — 2026-11-26
Stable #26 exact 0fa786aa55266bdded0e30eacfcc70e24e279eaa, [run 45809656420](https://github.com/mohammadrezamie/mano-studio/actions/runs/45809656420), all steps SUCCESS. Actual Setup and portable downloaded (artifact IDs 15122098723 / 15122253473), verified outer ZIP CRC, inner 324 entries, exact manifest sizes and hashes, 113 binary hashes, eight notice hashes and Python license. Setup 36,687,636 bytes SHA256 0e6dbcca2abb72ddf4caddc533a206b5feb52b2fd2b39b0bd5674ff4f61abd64; portable 53,486,334 bytes SHA256 3456b4a7d659689706800592a4d206403956c0af249062237a5801481fc50ba1. Outer SHA256 9744eda186317e074fc6f3f51519a42f2698d71cd5056c1cacd465858f17717d (Setup), 22639ec62d514e954d27a5b1617f67508c65adaca88e50e75fbd6d91b2c0f1c9 (portable). Both smoke PASS. Exact standalone academic source hash unchanged. Setup unsigned. No Virtual Keyboard paths remain. Restricted-PATH installed probe confirms private Python 3.14.10/Qt/SSL DLLs and three app-local VC runtime paths; no separate developer tool dependency in hosted runner. Native clean/pre-equipped Windows acceptance still pending.
P0 outstanding: installed ssl.OPENSSL_VERSION = 3.5.9, two embedded crypto DLLs 3.5.9; build report 3.5.0 requires explanation, all below November 24 review baseline 3.5.10. Qt 6.12.1 announced but publicly listed PySide6 wheels remain 6.12.0 at inspection; no patched compatible wheel confirmed. Official sources: https://www.openssl-library.org/news/vulnerabilities-3.5/index.html ; https://www.qt.io/blog/qt-6.12.1-released ; https://pypi.org/project/PySide6/ . No exploitability conclusion. Six LGPL package-specific flags remain; corresponding source controlled by distributor and exact module/third-party notices/relink rights unresolved (https://www.qt.io/development/open-source-lgpl-obligations). #26 advanced to bd5d353d4a39583acb92609c7c11d7ff701c6d29 with exact QtBase v6.12.0 GPL and LGPL text blobs 94a9ed024d3859793618152ea559a168bbcbb5e2 / 65c5ca88a67c30becee01c5a8816d964b03862f9 and packaging copy; no flag suppression or approval. New build pending; original #24 full regression preserved. No public release.
Beta 192fdf69a7615997b4ffa26a3019517ada2fc78a: validated session/draft/sample replacement now invokes Save/Discard/Cancel for dirty state, even empty dirty draft; clean nonempty state uses Yes/No, invalid incoming file rejected first. Eight actual local policy tests passed 0.03s, exact blobs 01a0a357d4361a0a254af9273bbada180644cfc2 / c35aebc6b69ce22b76447b261c36ed81ea202983. Two Qt locale cases added; not run locally. Reconciled #25 c38c8d258bef1271bec70ac1897544322965b31a and #27 09fd85c05780cd5c7d4e3584a8e472ccfdb51ff4 with all visual/QA changes retained. No new issue or PR.

## Source review and full memory inspection — 2026-11-26
Stable: actual successful #26 portable 0fa786aa source-family review covers all 113 binary names, 20 tested classifier cases (0.04s). Ordinary PE imports independently parsed for all 113. PDF/QML/Quick candidates are not cleared for removal; dynamic/delay imports and plugin paths still need verification. See docs/FROZEN_SOURCE_FAMILIES.md. Rechecked published Python and PySide6 listings: 3.14.10 and 6.12.0 respectively at inspection; no patched compatible replacement established. GPL/LGPL text rebuild 45832491036 remains queued. Qt corresponding-source and security gates remain open; no public release.
Beta exact bc6a9a75a2f073600e3f6486a0c017dfd03c39b5 adds one selected 16-word read-only memory page across all 4,096 addresses, merged with assembled/accessed addresses; no accumulation of old pages, no CPU state mutation. Strict hex address parser accepts Persian/Arabic digits and optional 0x, reused for breakpoints. 24 local model tests passed (0.04s), exact verified blobs 00946887e3b139400c062ef2a2c93756ad1d9626 and 7317098979f2b9e5c2d5d636ac74df318ec4ab95. Two locale Qt tests authored but unexecuted locally. Visual #25 head 20553a14c2f5eb255f2a336576eefa6d35ad56e2 and QA #27 head 2f7179ceadbfd21b2e9ed5ceaa44eac07f16b214 reconciled and mergeable. No new PRs or issues.

## License bundle, lean payload trial, memory report — 2026-11-26
Stable exact bd5d353d4a39583acb92609c7c11d7ff701c6d29 run 45832491036 succeeded, including installed smoke. Downloaded actual artifacts 15124967458 (Setup) and 15125485979 (portable), outer CRCs and 328 inner entries verified; all 113 binary hashes matched inventory. Setup 36,696,120 bytes SHA256 7b5012cbe5c80000dfcbcf5f6735fb77a4880ada38d460674db2b7e706c89ae3; portable 53,506,210 bytes SHA256 13c6a05ead34850071234a41a0d60ce679f5590e9f37814b068df25cbb1f76af. Packaged GPL/LGPL text normalized from CRLF matches exact upstream Git blobs. Installed runtime still OpenSSL 3.5.9, three crypto flags and six package notice flags remain. Native acceptance false. New opt-in lean PDF experiment source 1cc06b639ae4eded8f38e210865a9d0def1ecb9f; exact pair 4,665,968 bytes (2,544,993 compressed in previous portable). 8 local fixture tests passed (0.05s), exact blobs bfc8bef0bcdabffd6904f760fe0ddaed8d6f3752 / 454187289216f6dcbffd509260851336fe9b7ce4. Read-only actual archive copy plan with objdump ordinary imports succeeded. Windows ordinary+delay pefile check, actual reduced build and smoke remain pending; only redistribution PR opts in, default unchanged. Previous full payload preserved. No security or license approval.
Beta exact 5230c7077ade63bf4106cbb2ad48c5ea2ad6687a exports visible memory to atomic CSV with hex address/word, unsigned/signed decimal and binary; 11 local tests passed (0.04s), exact blobs 40207cb8f859e2bf5a9d5e9b02437117b38c4cd2 / 6f4e7301544735e4b965d6f58c964a6279e502af; two Qt locale cases authored, unexecuted locally. Not a full dump or checkpoint. #25 3694bec66fc65b902369a9295628b50b1b65040b and #27 92704015751ea63dd712c41c69e7354f13be56fc reconciled. No new issues/PRs or changes to original release candidate.


## Current product priorities
Build the polished, reliable desktop application on two parallel tracks. The [standalone RTL translator](rtl_translator.py) remains individually downloadable and standard-library-only; the owner handles academic explanation separately. No mandatory 1.0.0 deadline. See [current channel policy](docs/DEVELOPMENT_CHANNELS.md).

## Independent in-app update channels — 2026-11-26
Both product tracks now filter updates before selecting version/asset metadata. Stable accepts newer final non-prerelease tags; Beta accepts newer explicitly marked beta/rc only. No dev/alpha, draft, ambiguous flags, downgrade or automatic channel switching. The installed version determines the channel, shown in Persian/English preferences; users may manually choose a different channel via official Releases. No startup network requests or automatic installer execution. Stable candidate #26 exact 767086599ab405d6e68590459842671678abbf00 and Beta adad4365336883bda4f78064797bd714550cdaeb: each passed 39 local tests (30 shared policy + 9 mock HTTP service tests) on actual updated service sources; Stable 0.09s, Beta 0.06s. Exact tested service blobs 58c5b1cab6bce8aabdda514060d3a99ebbd19e07 / 17c21d491eee611ba1b3111e2198cfea721b648e; shared model/test blobs 009e2fd62e3758d626163ee86bde22a0410701e6 / e9a650662db7c87a1c27eee14159bb643cd412b6 / fb527190dd4b6a53ff7df0e21c82ec5bf20d346d. Beta unchanged real download module 097087b44423260cbf50f31889f545e2ba8d3680. New UI and frozen build not tested locally. #25 ad2f32109864a5b4b9c5fd874b0a010a875ba1a1, #27 bd02c62ee90b55e58d6da1e5b5032817119d385c reconciled with all visual/evidence changes. Prior lean artifact 1cc06b639 retained; new Stable head requires fresh Windows build and applicable regression. Security, redistribution, native acceptance remain open. No public release, version renumbering or translator change.

## Compact memory navigation — 2026-11-26
Beta 766e7f9dccfd5bc9c972d1a35362fedd66521895 separates address/page controls from memory actions, adds previous/next navigation, disables unavailable actions and uses LTR technical tables with bilingual accessible address name. All 256 pages tested in both directions without wrapping. 23 local pure tests passed in 0.04s; exact tested blobs ccd5f43dc12a9f56e8fafba2394ce37db65bc8aa and 4dbd0344a2f79cf27b473b55e5b8c77b13eb194a, existing memory inspector blob 00946887e3b139400c062ef2a2c93756ad1d9626. Two bilingual Qt tests authored; Qt unavailable locally, layout and native acceptance not confirmed. Visual PR #25 0db58b8cf1c8818f3a67ef58f14fdea0489a2f12 and #27 745587a533f45626877e91899023f95bacc83c21 retain all prior 11/10 changes. Stable updater candidate 767086599ab405d6e68590459842671678abbf00 run 45849518732 at inspection: [{"status":"completed","conclusion":"success","failed":[]}]. No Stable code changed this turn; no public release or translator changes.

## Incremental memory UI and Stable verification — 2026-11-26
Beta 37815b6c208b7d73c3fb1ea09bd633aadd0a9c23 adds incremental memory row refresh and selection preservation, clears stale cache/controls after failed or empty assembly, disables memory editing during incomplete instruction. All 13 local pure tests passed (0.04s), exact tested blobs 0d2399d1968f7b71fc2d1cbf5344b84175fd8e36 / 37063f4ffcec2b8dd4f66ab3664b4d25c8cfa9cc. A single changed word among 4096 rows plans one row update instead of all rows, not measured GUI latency. Two bilingual Qt cases authored, not executed locally. Visual #25 5e0168722637dc2a202a2832a2e75e20c7566640 and #27 d5102f03273ad2ac9b2a5d56249996e0b657530a retain all 11/10 prior changes. Stable head 3324ab5dbaabc54c6207305618f57bdb5e967599 preserved; live checks [{"run_id":45851712083,"jobs":[{"name":"test (windows-latest)","status":"in_progress","conclusion":null,"step":"Run python -m pytest -q --durations=25 --junitxml=regression.xml","failed":[]},{"name":"test (ubuntu-latest)","status":"queued","conclusion":null}]},{"run_id":45851712631,"jobs":[{"name":"installer","status":"completed","conclusion":"success","failed":[]}]}]. Security, corresponding source and native Windows acceptance remain open. No forced version/date; no public release. Translator unchanged.
