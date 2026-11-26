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
