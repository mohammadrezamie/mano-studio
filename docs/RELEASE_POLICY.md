# Permanent four-lane delivery policy — owner directive 2026-11-27

This section supersedes conflicting historical scheduling/approval language below.

1. **Stable publication**: publish the verified stable candidate as a real public GitHub Release with Windows x64 Setup, Portable, checksums, honest compatibility and release notes; close applicable security, redistribution, authenticity and install/upgrade gates for the exact bytes.
2. **Beta publication**: independently publish the verified forward beta as a public prerelease with the same distribution discipline. Beta remains ahead of Stable.
3. **Stable updates**: continuously maintain the next stable patch on a separate maintenance branch; prioritize reliability, security, compatibility and tested fixes, with independent acceptance.
4. **Beta updates**: continuously develop, test and integrate the forward feature line; promote only verified changes to Stable when appropriate.

All four lanes remain active concurrently. Do not wait for unrelated feature PRs to publish a qualified previous version; do not replace a frozen release candidate merely to add features. Owner authorizes public releases once applicable gates pass, not a false approval of failed or missing evidence. Maintain the English README download matrix and GitHub Releases metadata. No invented progress percentages or background assistant work.

## Manual download authenticity versus automated installation

Manual public Setup/Portable distribution does not inherently require a paid Authenticode certificate. If no reviewed publisher signing identity is available, a manual-download release may be considered only after all other applicable exact-byte gates pass, the build provenance and SHA-256 checksums are verified, and release notes prominently identify the installer as unsigned, describe possible Windows reputation warnings, and direct users to the official GitHub repository. Hashes alone do not establish independent publisher identity. Never advise users to disable protection. Record the residual risk and the actual authenticity review decision for each release. This distinction does not authorize a release with unresolved security, corresponding-source, notice, or native acceptance evidence. Automated in-app installation stays fail-closed until trusted publisher identity and end-to-end upgrade acceptance are available.

## Update Center — both channels

Owner requests complete in-app notification, download and installation. Preserve offline core behavior. Offer an explicitly opt-in automatic update check (off by default; bounded nonblocking GitHub requests only), plus manual check. Notify about eligible public newer releases for installed channel only. Show version, notes, size, download progress, cancellation, and explicit Download & Install confirmation. Verify expected official asset URL/name/platform, digest/length and independently trusted publisher identity; SHA-256 from the same release is integrity, not publisher authentication. Reject unsigned, untrusted, tampered, wrong-channel or older installers for automated launch. Preserve preferences/files, prompt to save unsaved work, distinguish Setup from Portable, verify clean upgrade and failure recovery; no silent execution or forced restart. Manual link remains available. No credentials, signing key or publisher identity invented; keep installation disabled until trust provisioning and end-to-end Windows tests pass. Record current status honestly.

---

# Product comfort and pre-release policy
Owner decisions, 2026-11-24. Applies to all development branches and supersedes older release targets.
## Calm by design
Mano Glass is the visual identity, but avoid visual noise, excessive glow, flashing, constantly moving backgrounds, and decorative loops. Use restrained gradients, high-contrast opaque editor surfaces, whitespace and consistent hierarchy. Animation is purposeful and only active on interaction or during a simulation. Keep the live lab separate from the normal editing workflow. Offer three themes (Light, Dark, Night), a persisted reduced-motion switch that disables nonessential transitions and bus animation, and a persisted glass-effects switch for a plain, readable fallback. Respect OS reduced-motion when feasible. No artificial splash delays.
## Offline and online
Owner clarification: the application is ALWAYS offline for all core functions, with no login, cloud service, telemetry or startup/background request. Only an explicit Check for updates button may make a bounded HTTPS request to the official GitHub release API; no global online mode or persistent permission needed. Never upload user files or silently download/install. Show the official releases URL if a newer version exists. No connection or failed checks must not affect offline tools. Animation, glass assets, and help are bundled/local. Prefer Qt procedural animations driven by actual CPU state; optional original generated artwork or pre-rendered Remotion clips may be bundled only if useful, licensed and lightweight, never streamed. No decorative looping videos or new runtime dependency for beta.
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

## Owner question — in-app update installation
Target UX: explicit Check for updates, display version/release notes/download size, user chooses Download and install. Preserve local settings and documents; prompt to save before shutdown. Only official GitHub release assets, HTTPS, expected platform/version, bounded download, cryptographic authenticity (trusted signing key or Windows Authenticode with pinned publisher), SHA-256 integrity, staging and verification before execution. Hash from same release alone is not publisher authentication. Reject missing or invalid signatures and never execute arbitrary downloaded files; keep installed version on failure. No unattended startup check, silent install, forced upgrade or public release. Existing check-only UI remains until trusted signing/build and clean install/upgrade rollback tests exist.

Current implementation increment: user-triggered check fetches bounded release metadata, displays notes as plain text and indicative installer size when unambiguous, and offers an explicit official releases page button. Download/install stays disabled until a trusted installer verification and upgrade process is validated. Release text is publisher-provided, not automatically translated.

## Owner quality-first override (2026-11-24)
No arbitrary application or installer size cap. Previous guidance about lightweight assets and avoiding new dependencies is a preference superseded where verified quality warrants a larger asset or additional technology. Any new dependency or asset still requires compatible license, provenance, offline operation, security review, graceful fallback and a concrete benefit; responsiveness and accessibility remain quality requirements. No network at startup, telemetry, duplicated engines, or release/installer work without authorization.
