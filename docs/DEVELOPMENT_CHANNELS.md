# Two-channel development and release policy

Owner decision — 2026-11-26. **Exactly two permanent product plans: Stable and Beta.** This supersedes conflicting historical plan names. Short-lived feature/quality branches, documentation and fallback artifacts are not additional product channels.

| Channel | Canonical plan | Integration branch | Active work |
|---|---|---|---|
| Stable | [#4](https://github.com/mohammadrezamie/mano-studio/issues/4) | `main` (accepted source; not necessarily a published release yet) | `release/v1-candidate` [#24](https://github.com/mohammadrezamie/mano-studio/pull/24); redistribution [#26](https://github.com/mohammadrezamie/mano-studio/pull/26) |
| Beta | [#23](https://github.com/mohammadrezamie/mano-studio/issues/23) | `develop/next-beta` | typography [#25](https://github.com/mohammadrezamie/mano-studio/pull/25), visual evidence [#27](https://github.com/mohammadrezamie/mano-studio/pull/27), curriculum and feature issues |

## Stable
Publish and maintain the latest verified stable version. Current target is v1.0.0; classroom target November 30, 2026 is conditional, not a promise. Keep changes release-focused: correctness, reliability, installability, visual acceptance, legal redistribution, documentation, and appropriate tested features. Require exact-commit tests, native Windows acceptance, artifact identity, licensing review and verified release notes. After first release, maintain stable fixes in the same channel.

## Beta
Develop the latest features continuously, including full textbook coverage, real experiments, bilingual design, offline behavior, and saved examples. Integrate reviewed feature branches into the Beta branch; verify the exact integrated build before publishing a clearly identified prerelease. Use version numbers appropriate to the verified baseline and scope; do not promote an old packaging artifact as the latest Beta. New feature work must not block stable delivery.

## Promotion and history
Selectively promote tested Beta improvements to a stable candidate; do not merge unverified Beta wholesale. Port relevant stable fixes back to Beta. Preserve the standalone `rtl_translator.py`, all useful history, resources, branches and test evidence. No branch deletion, forced history rewrite, issue deletion or closure of unfinished tasks for cosmetic cleanup. Close a superseded PR only after verifying ancestry/retention and link the successor. Historical fallback [#22](https://github.com/mohammadrezamie/mano-studio/pull/22) is retained as a stable-delivery contingency while acceptance is pending; [#19](https://github.com/mohammadrezamie/mano-studio/pull/19) is closed as superseded after confirming its head has zero unique commits relative to #22. The branches and discussions remain.

## GitHub organization
- Two canonical plan issues, no competing permanent roadmap issues. Feature issues stay open until acceptance, with history intact.
- Every active issue and PR has a `track: stable` or `track: beta` label (both for shared documentation), and a matching title prefix. `plan` identifies the two central issues; `fallback` and `superseded` are lifecycle labels, not channels.
- [Stable issues](https://github.com/mohammadrezamie/mano-studio/issues?q=is%3Aissue+is%3Aopen+label%3A%22track%3A+stable%22) · [Beta issues](https://github.com/mohammadrezamie/mano-studio/issues?q=is%3Aissue+is%3Aopen+label%3A%22track%3A+beta%22)
- [Stable PRs](https://github.com/mohammadrezamie/mano-studio/pulls?q=is%3Apr+is%3Aopen+label%3A%22track%3A+stable%22) · [Beta PRs](https://github.com/mohammadrezamie/mano-studio/pulls?q=is%3Apr+is%3Aopen+label%3A%22track%3A+beta%22)
- Keep each plan's current checklist concise. Append history/evidence in linked documents or comments; preserve prior text in collapsed historical sections. Update existing issues rather than opening duplicates.
- Shared documentation PR [#20](https://github.com/mohammadrezamie/mano-studio/pull/20) is not a third channel. Do not disturb active candidate CI for documentation cleanup.

## Current evidence
As checked during the reorganization: Windows installer and portable smoke passed for exact v1 candidate #24; full regression and public distribution approval are not confirmed. PR #26 implements a proposed redistribution preflight and dependency remediation, not an accepted rebuilt installer. #25 and #27 remain Beta drafts awaiting integrated Qt evidence. No public Stable or latest Beta release is confirmed. Follow the plans and [Releases](https://github.com/mohammadrezamie/mano-studio/releases) for current status.

This policy does not change executable code, academic deliverables, version tags, visibility, or release approval.

## Stable/Beta progress — 2026-11-26
Stable: actual original 112-binary archive classified; Python _ssl/_hashlib import older OpenSSL 3.0.16, public support ended September 7, 2026. OpenSSL 3.5.9 variant also requires recent advisory review. See [binary security review](STABLE_BINARY_SECURITY_REVIEW.md). #26 queued internal build retained; no security clearance or release. Next candidate must use a maintained Windows runtime and verified supported/patched dependencies, plus native and full regression. Beta: develop/next-beta source d4e673c74c141154a909089807c55f404d97e72b adds five saved .mano assembly samples and bilingual Computer menu, with 14 exact-source local tests (including actual CPU results) passed. Guide and evidence updated at 0e28fc35a7f4cac1091b1c24ffa5a48166cf178a; Qt/integration pending. Both plans remain independent; no new issue/PR.

## Permanent owner requirement — easy standalone installation (2026-11-26)
Both Stable and Beta require a one-step offline Windows Setup, no manual Python/Qt/pip or other prerequisite installation, no reinstall of compatible shared prerequisites, and no global PATH changes or destructive upgrades. Private bundled libraries are intentional for isolation. See docs/STANDALONE_INSTALLATION.md. This is a mandatory release gate (#4/#23/#10), not a completed native acceptance claim. #26 commit 3180a91c6d92e96e6648fe991cd9f10e7b49ea60 adds sanitized installed-process PATH, loaded private Python/Qt/SSL DLL checks and actual SSL version report; 3 local path tests passed in 0.04s with exact blobs e8fe55b4827bc00fef9493861d6ee8ba1d6ad567 and 2fa08d4579a9a0f0ee71402e40e94828c65c34be. Windows diagnostic and clean/pre-equipped VM tests pending. #25 and #27 reconciled without deleting changes, verified mergeable at ec309ca1842855c5b2fd62690f867166e1902722 and 9e805a5c52f488c81a5ae4a10d5e541f77997236. No product PR merged or release published.
