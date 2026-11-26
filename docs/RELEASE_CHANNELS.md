# Mano Studio release channels

## Version line policy

Beta is always the forward development line and must compare higher than the current Stable version under the project's SemVer ordering. A Beta prerelease is not a lower-numbered copy of Stable.

| Track | Branch | Current internal/candidate version | Public release form |
| --- | --- | --- | --- |
| Stable | `release/v1-candidate` | `1.0.0` candidate | `v1.0.0` final, only after all Stable gates and owner approval |
| Beta | `develop/next-beta` | `1.1.0-dev.1` | `v1.1.0-beta.1` prerelease, only after Beta gates and owner approval |

## Update isolation

The installed version determines its channel. Stable accepts only newer, non-prerelease final tags. Beta accepts only newer explicitly marked beta or release-candidate tags. Development and alpha tags are not offered as public updates. A Beta build never silently downgrades or changes channel to Stable; a Stable build never installs a Beta build. The updater contacts GitHub only after the user explicitly requests an update check.

## Promotion model

1. Keep `develop/next-beta` moving independently; new features and experiments stay here.
2. Freeze an exact Beta candidate from a tested Beta commit, change only the candidate version to `1.1.0-beta.1`, rebuild, and rerun the exact-source Windows/Ubuntu and installer gates.
3. Promote Beta to Stable only after a separate acceptance decision. Beta features are not merged into `release/v1-candidate` by default.
4. Once Stable 1.1.0 is accepted and published, start the next forward Beta line at 1.2.0-dev.1.

Version ordering does not establish readiness. Security, redistribution, signatures, clean-machine installation, native bilingual acceptance, source integrity and explicit owner approval remain mandatory. No release is published by this document or by a passing CI run.
