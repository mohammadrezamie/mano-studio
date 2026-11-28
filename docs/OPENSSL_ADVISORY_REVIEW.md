# OpenSSL advisory applicability review — 2026-11-28

## Exact bundled runtime and patch status

The frozen Windows candidates contain OpenSSL **3.5.9**. The official OpenSSL 3.5 vulnerability index marks versions from 3.5.0 through versions before 3.5.10 as affected by several November 2026 issues. The OpenSSL project announced that 3.5.10 is a security-fix release scheduled for **1 December 2026, 13:00–17:00 UTC**. It is not yet published as of this review. Do not claim current candidates contain it, install an unpublished artifact, or silently change the dependency pin.

Sources:
- Official vulnerability index: https://www.openssl-library.org/news/vulnerabilities-3.5/
- Official release timeline: https://www.openssl-library.org/news/timeline/
- OpenSSL project announcement (24 Nov): https://www.openwall.com/lists/oss-security/2026/11/24/14

## November advisory inventory

All issues below are Low severity in the upstream index. An affected library version does not by itself prove that every application embedding the library is exploitable; each issue has an API, protocol or configuration precondition.

| CVE | Date | Vulnerable path / precondition | Mano Studio source-level assessment |
| --- | --- | --- | --- |
| CVE-2026-88822 | 10 Nov | QUIC automated peer detection | The app uses ordinary HTTPS for explicit update checks; no QUIC connection is created |
| CVE-2026-88823 | 10 Nov | AES-GCM-SIV AAD split across updates including an empty update | No direct AES-GCM-SIV or EVP cipher API use identified in application source |
| CVE-2026-107496 | 10 Nov | CMS encryption to attacker-controlled EC certificate with group order 1 | No CMS encryption workflow or direct CMS API use identified |
| CVE-2026-95691 | 10 Nov | QUIC client handling of retransmitted CRYPTO frames | No QUIC client or direct OpenSSL QUIC API use identified |
| CVE-2026-95692 | 10 Nov | AES-GCM-SIV initialized with a non-standard IV length | No direct AES-GCM-SIV or EVP cipher API use identified |
| CVE-2026-107493 | 17 Nov | PEM_X509_INFO_read_bio_ex() with a non-NULL caller-owned stack followed by failed read | No direct call identified. OpenSSL says its own TLS CA-loading callers pass NULL; third-party callers still require review |
| CVE-2026-124709 | 17 Nov | QUIC server retains rejected streams after peer resets | The app does not expose an OpenSSL QUIC server |
| CVE-2026-35190 | 17 Nov | TLS 1.3 server using SSL_CTX_set_cert_flags(...SSL_CERT_FLAG_SUITEB_128_LOS) | The app is an HTTPS client; no such server-side Suite B flag is configured in application source |
| CVE-2026-84785 | 24 Nov | QUIC receiver accepts peer-initiated streams with out-of-order fragments | The app does not create a QUIC server or accept QUIC streams |
| CVE-2026-107494 | 24 Nov | QUIC RETIRE_CONNECTION_ID frame queue | No QUIC connections are created by the app |
| CVE-2026-121482 | 24 Nov | CMS/PKCS#7 verification with CRL checking explicitly enabled | The app does not process CMS/PKCS#7 content or set OpenSSL CRL_CHECK |
| CVE-2026-84786 | 24 Nov | DANE-enabled TLS client combining DANE PKI with traditional PKI and affected TLSA usages | The app uses ordinary HTTPS and does not enable OpenSSL DANE APIs |

This is a bounded **source-level reachability review**, not a vendor-issued exemption, complete audit of PySide6/Qt internals, or independent penetration test. A no-direct-call finding is not proof that the transitive native dependency is free of vulnerabilities. Qt and Python remain part of the runtime trust boundary.

## Release gate

1. Keep exact 3.5.9 runtime version, binary hashes, Python runtime tuple and provenance evidence attached to each candidate. Python 3.14 reports OpenSSL 3.x as `(major, minor, fix, patch, status)`; `(3, 5, 0, 9, 0)` means 3.5.9. The normalizer must use tuple element 3 for the patch number.
2. Keep the automated review baseline at 3.5.10. Below-baseline evidence must remain flagged. Synthetic 3.5.10 fixtures test parsing only; they do not prove a fixed binary is available.
3. **No calendar-based release hold.** Owner directive, 2026-11-28: finish and publish each initial channel as soon as its actual exact-byte release gates pass. 1 December is an upstream forecast, not a Mano Studio launch prerequisite. Assess the currently shipped binaries and transitive paths now. Either (a) document an independent, evidence-backed disposition of every applicable advisory for the exact current bytes, including residual exposure and any necessary mitigation, or (b) use an already published, compatible, verified patched runtime or source fix. If neither route closes an applicable risk, keep only the affected candidate blocked and identify the unresolved advisory. Do not treat a low severity label or lack of direct application calls as clearance.
4. If a runtime or package changes, verify its published provenance and hashes, rebuild the affected channel, and rerun full cross-platform regression, offline Portable smoke, exact Setup install/uninstall smoke, runtime evidence, redistribution checks and native acceptance against those same bytes. Reuse verified exact-byte evidence when the bytes and acceptance conditions are unchanged; do not restart tests for unrelated feature work.
5. When 3.5.10 is actually published, independently review its full advisory set, provenance, compatibility and embedded runtime; prioritize validated remediation in the separate 1.0.1 / 1.1.0-beta.2 update lanes if initial releases already qualify. Never label an unverified fix as installed. Qt source/notice/relink and native acceptance gates remain independent.

The current checker intentionally never sets `security_approved=true` or `public_release_approved=true`. A copied OpenSSL LICENSE notice is attribution evidence only; it is not a security fix, source correspondence or redistribution approval.
