# OpenSSL advisory applicability review — 2026-11-28

## Exact bundled runtime and patch status

The frozen Windows candidates contain OpenSSL **3.5.9**. The official OpenSSL 3.5 vulnerability index marks 3.5.0 through versions before 3.5.10 as affected by several November 2026 issues. OpenSSL's project team announced that 3.5.10 is a security-fix release scheduled for **1 December 2026, 13:00–17:00 UTC**. As of this review date it is not yet published; do not claim the candidates contain it, install an unpublished artifact, or silently change the dependency pin.

Sources:
- Official vulnerability index: https://www.openssl-library.org/news/vulnerabilities-3.5/
- Official release timeline: https://www.openssl-library.org/news/timeline/
- OpenSSL project release announcement (24 Nov): https://www.openwall.com/lists/oss-security/2026/11/24/14

## Advisory inventory and application-path assessment

The upstream index lists the following November issues as affecting the 3.5 series before 3.5.10. All listed issues below are Low severity. The upstream affected-version range is a library-level statement; it does **not** prove that every application embedding that library is exploitable. Each issue has an API, protocol, or configuration precondition.

| CVE | Published | Vulnerable path / precondition | Mano Studio source-level assessment |
| --- | --- | --- | --- |
| CVE-2026-88822 | 10 Nov | OpenSSL QUIC automated peer detection | The app uses ordinary HTTPS for explicit update checks; it does not create QUIC connections |
| CVE-2026-88823 | 10 Nov | AES-GCM-SIV AAD supplied in chunks, including an empty update | No direct AES-GCM-SIV or EVP cipher API use identified in application source |
| CVE-2026-107496 | 10 Nov | CMS encryption to an attacker-controlled EC certificate with group order 1 | No CMS encryption workflow or direct CMS API use identified |
| CVE-2026-95691 | 10 Nov | QUIC client handling of retransmitted CRYPTO frames | No QUIC client or direct OpenSSL QUIC API use identified |
| CVE-2026-95692 | 10 Nov | AES-GCM-SIV initialized with a non-standard IV length | No direct AES-GCM-SIV or EVP cipher API use identified |
| CVE-2026-107493 | 17 Nov | PEM_X509_INFO_read_bio_ex() called with a non-NULL, caller-owned stack and then a failed read | No direct call identified. OpenSSL states its own callers, including TLS CA loading, pass NULL; this does not replace review of third-party callers |
| CVE-2026-124709 | 17 Nov | OpenSSL QUIC server retaining rejected streams after peer resets | The app does not expose an OpenSSL QUIC server |
| CVE-2026-35190 | 17 Nov | TLS 1.3 server configured with SSL_CTX_set_cert_flags(...SSL_CERT_FLAG_SUITEB_128_LOS) | The app is an HTTPS client and no such server-side Suite B flag is configured in application source |
| CVE-2026-84785 | 24 Nov | QUIC receiver accepting peer-initiated streams with out-of-order fragments | The app does not create a QUIC server or accept QUIC streams |
| CVE-2026-107494 | 24 Nov | QUIC RETIRE_CONNECTION_ID frame queue | No QUIC connections are created by the app |
| CVE-2026-121482 | 24 Nov | CMS/PKCS#7 verification with CRL checking explicitly enabled | The app does not process CMS/PKCS#7 content or set OpenSSL's CRL_CHECK verification flag |
| CVE-2026-84786 | 24 Nov | DANE-enabled TLS client combining DANE PKI with traditional PKI and affected TLSA usages | The app uses ordinary HTTPS and does not enable OpenSSL's DANE API |

This is a bounded **source-level reachability review**, not a vendor-issued exemption, a complete audit of PySide6/Qt internals, or an independent penetration test. A no-direct-call finding must not be presented as proof that the transitive native dependency is free of vulnerabilities. In particular, the application still ships the affected library version, and Qt/Python are part of the runtime trust boundary.

## Release gate and next action

1. Keep the exact 3.5.9 runtime version, binary hashes, Python runtime tuple, and provenance evidence attached to each candidate. Python 3.14 reports OpenSSL 3.x as `(major, minor, fix, patch, status)`; `(3, 5, 0, 9, 0)` means 3.5.9. The normalizer must use tuple element 3 for the patch number.
2. Keep the automated review baseline at 3.5.10. Below-baseline evidence must remain flagged. Synthetic 3.5.10 fixtures validate parsing only; they do not prove that a fixed binary is available.
3. On or after the announced release window, verify the official 3.5.10 publication and its signature/checksums, update the exact wheel/runtime pins only from verified published artifacts, rebuild both Stable and Beta candidates, then inspect the actual embedded OpenSSL binaries and their hashes.
4. Re-run the complete cross-platform regression, offline portable smoke, exact Setup install/uninstall smoke, runtime evidence, redistribution checks, and the native acceptance handoff against the **same new candidate bytes**.
5. Independently review the full 3.5.10 advisory set and transitive Qt/Python call paths. Do not waive an issue merely because the app does not directly invoke its API.

The current checker intentionally never sets `security_approved=true` or `public_release_approved=true`. A copied OpenSSL LICENSE notice is attribution evidence only; it is not a security fix, source correspondence, or redistribution approval.
