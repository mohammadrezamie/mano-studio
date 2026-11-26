# Product comfort and pre-release policy

## Current controlling owner policy — 2026-11-26

This instruction supersedes conflicting historical deadlines, version targets, beta-only timing restrictions, development-only restrictions and academic-defense expansion requirements.

- Maintain exactly two permanent tracks in parallel: Stable (#4) and Beta (#23). Publish each independently when its applicable acceptance gates are met; Beta publication is optional and must be explicitly marked prerelease. Do not make Stable wait for the entire textbook or Beta scope.
- No mandatory v1.0.0 or fixed release date. The existing internal v1.0.0 candidate and verified artifacts remain valid historical evidence; choose the public version appropriate to the accepted scope and release history. Never rename an unverified artifact to imply stability.
- Stable means a genuinely reliable, polished, integrated application: verified exact-revision correctness, UI usability in Persian and English, offline behavior, standalone Windows install/upgrade/uninstall, security, redistribution and artifact authenticity. Freeze or defer unverified features rather than lower acceptance standards.
- The academic deliverable is exactly the standalone root `rtl_translator.py`: one downloadable Python file, standard library only, no sibling imports, Qt, simulator or network. Keep the desktop app calling this same core. The owner will independently learn the line-by-line explanation and prepare the defense. Do not prioritize additional defense tutorials, separate academic applications or presentation workflows over product development. Existing useful docs/examples remain available.
- Primary effort: build, integrate, improve and test the actual desktop application, premium readable bilingual UX and practical labs. Keep documentation concise and evidence-backed, not a substitute for implementation. Preserve zero-manual-prerequisite Setup and offline-first operation.
- Do not claim a release until actual publication and verification; retain all existing acceptance and security gates. No new fixed deadline, public version tag or release is created by this policy update.

Owner decisions, 2026-11-24. Applies to all development branches and supersedes older release targets.
## Calm by design
Mano Glass is the visual identity, but avoid visual noise, excessive glow, flashing, constantly moving backgrounds, and decorative loops. Use restrained gradients, high-contrast opaque editor surfaces, whitespace and consistent hierarchy. Animation is purposeful and only active on interaction or during a simulation. Keep the live lab separate from the normal editing workflow. Offer three themes (Light, Dark, Night), a persisted reduced-motion switch that disables nonessential transitions and bus animation, and a persisted glass-effects switch for a plain, readable fallback. Respect OS reduced-motion when feasible. No artificial splash delays.
## Offline and online
Owner clarification: the application is ALWAYS offline for all core functions, with no login, cloud service, telemetry or startup/background request. Only an explicit Check for updates button may make a bounded HTTPS request to the official GitHub release API; no global online mode or persistent permission needed. Never upload user files or silently download/install. Show the official releases URL if a newer version exists. No connection or failed checks must not affect offline tools. Animation, glass assets, and help are bundled/local. Prefer Qt procedural animations driven by actual CPU state; optional original generated artwork or pre-rendered Remotion clips may be bundled only if useful, licensed and lightweight, never streamed. No decorative looping videos or new runtime dependency for beta.
## Owner question — in-app update installation
Target UX: explicit Check for updates, display version/release notes/download size, user chooses Download and install. Preserve local settings and documents; prompt to save before shutdown. Only official GitHub release assets, HTTPS, expected platform/version, bounded download, cryptographic authenticity (trusted signing key or Windows Authenticode with pinned publisher), SHA-256 integrity, staging and verification before execution. Hash from same release alone is not publisher authentication. Reject missing or invalid signatures and never execute arbitrary downloaded files; keep installed version on failure. No unattended startup check, silent install, forced upgrade or public release. Existing check-only UI remains until trusted signing/build and clean install/upgrade rollback tests exist.

Current implementation increment: user-triggered check fetches bounded release metadata, displays notes as plain text and indicative installer size when unambiguous, and offers an explicit official releases page button. Download/install stays disabled until a trusted installer verification and upgrade process is validated. Release text is publisher-provided, not automatically translated.


## Owner quality-first override (2026-11-24)
No arbitrary application or installer size cap. Previous guidance about lightweight assets and avoiding new dependencies is a preference superseded where verified quality warrants a larger asset or additional technology. Any new dependency or asset still requires compatible license, provenance, offline operation, security review, graceful fallback and a concrete benefit; responsiveness and accessibility remain quality requirements. No network at startup, telemetry, duplicated engines, or release/installer work without authorization.


## Owner update download request — 2026-11-26
Next-generation branch now implements explicit download-only for eligible official assets with GitHub SHA-256/size, strict URL and redirect validation. This supersedes check-only for that branch, not the frozen first beta. Never execute a downloaded installer until trusted publisher verification and upgrade acceptance exist. Native Windows association and actual Release download pending. See NATIVE_FILES_AND_UPDATES.md.


<details>
<summary>Superseded historical policy snapshots — retained for audit only</summary>

## Release rules
Until the owner reviews progress in class next week (calendar week 2026-11-30 through 2026-12-06), do not publish a stable release, tag v1.0.0, or advertise stability. Development builds and explicitly marked prereleases only. Current code identifies as 0.3.0-dev. Proposed next public test build v0.3.0-beta.1 or later 0.x beta, subject to CI, clean Windows installation/uninstallation smoke test, source inclusion and owner review. Never silently promote a prerelease to stable. After class, stable release still requires explicit owner approval and acceptance testing.
## Classroom target (planning, not commitment)
Prioritize a usable RTL-to-ASM beta with three input modes, all 25 documented instruction templates, bilingual help, persistent settings, restrained glass themes, readable translator source and Windows setup. The demo live lab is optional, not a blocker. Defer general-purpose simulator, reverse translation and advanced animations if they threaten the classroom demonstration. Report actual test/build status and unresolved risks.

## Latest owner override: development only
Do not pursue installer builds, release preparation, tags, public prereleases, or hands-on acceptance testing until the owner asks. Retain packaging code for later; automatic installer workflow is paused. Continue feature development and normal regression checks as appropriate, without blocking progress on distribution. Owner will perform manual testing at the appropriate stage. Classroom review is a progress review, not a release deadline. No release of any kind until explicit approval.

## Owner exception — first internal development candidate
Latest owner requests the first version built and testing in GitHub. Permit a single development candidate artifact and existing installer smoke on deliberate `build: candidate` commit (documented in docs/BUILD_CANDIDATE.md). No public release, tag, stable version, production deployment, or claim of visual signoff. Internal version 0.3.0-dev.1; later builds require deliberate candidate commit/manual dispatch.

## CI recovery override
Keep the proven simple Tests matrix; the alternative automatic candidate orchestration was not observable in the connected Actions results. Build candidate only via manual Windows workflow dispatch until a verified automatic route exists. Source application smoke is included in regression tests. No public release/tag, no claim of an executable until its artifact and smoke are verified.


## Owner priority override — first beta delivery, 2026-11-25
Owner requests reaching the initial GitHub release sooner. Freeze optional feature expansion for beta; prioritize existing RTL workflow, integrated visual PR #17 and correctness PR #16, exact-head regression and actual bilingual screenshots, then Windows x64 packaging and acceptance. Installer preparation and internal candidate builds are authorized again. Separate release/first-beta-candidate branch builds only temporary development artifacts initially, not a public tag or release. Exercise the known main baseline first; integrate verified PRs and rebuild the exact final commit before any publication. Proposed public version remains v0.3.0-beta.1, subject to successful portable/installed smoke, redistribution review, native acceptance and release approval. No stable publication. Do not imply a scheduled release or unattended assistant work.


## Integrated first beta candidate — 2026-11-25
Owner requests expedited initial prerelease with high quality. Isolated release/beta-integrated combines exact heads of #16, #17 and #18. No publication or stable claim. Independent source branches retained; combined CI is final source gate. Current version 0.3.0-dev.1; proposed public beta v0.3.0-beta.1. Verify actual Windows installer/portable artifacts, hashes, bilingual screenshots, native acceptance, redistribution/license and owner acceptance before publication. Freeze optional features. Fix obsolete About modal test and require all six actual About captures. No translator changes.


## 2026-11-26 owner deadline override
Target instructor-ready v1.0.0 on Monday 2026-11-30. Earlier beta-only timing policy is superseded, while evidence gates remain. Existing build.ps1 and candidate_manifest.py reject stable versions intentionally; stable candidate preparation must revise these guards and release-specific version tests, then rebuild and verify exact new head. See V1_DELIVERY_PLAN.md. No beta artifact renaming.

</details>


## Owner clarification — Beta must stay ahead of Stable (2026-11-27)

The owner explicitly requires the Beta line to remain semantically ahead of the Stable line. The current Stable candidate remains **1.0.0**; the ongoing next-generation Beta development line is **1.1.0-dev.1**, with the proposed first public prerelease **v1.1.0-beta.1**. This supersedes older draft references to v0.3.0-beta.1; no public GitHub release or tag has been published as of this checkpoint. Keep `develop/next-beta` independent from `release/v1-candidate`. Stable receives only separately reviewed and accepted fixes; Beta feature work is never copied into Stable automatically. The existing updater policy is channel-isolated: Stable accepts newer final releases only, while Beta accepts newer beta/RC releases only. When 1.1.0 is eventually promoted to Stable, the next Beta development line advances to 1.2.0-dev.1. These version numbers do not waive any testing, security, licensing, native acceptance or owner-approval gate.
