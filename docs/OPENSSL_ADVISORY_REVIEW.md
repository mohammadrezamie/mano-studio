# OpenSSL advisory applicability review — 2026-11-27

The candidate's Windows runtime contains OpenSSL 3.5.9, the latest published 3.5 patch on this date. OpenSSL announced 3.5.10 for 1 December 2026; it is not released yet, so the candidate must not pin to or claim use of 3.5.10 before publication. See https://www.openwall.com/lists/oss-security/2026/11/24/14 and https://mirror.openssl-library.org/news/timeline/.

A previous runtime evidence check misread Python's OpenSSL 3.x version tuple. Python reports (major, minor, fix, patch, status); the patch is element 4 (zero-based index 3). Python 3.14.10's (3, 5, 0, 9, 0) therefore represents OpenSSL 3.5.9, not 3.5.0. The checker now normalizes this correctly and still never marks a release approved.

The 24 November 2026 low-severity fixes scheduled for 3.5.10 concern:
- CVE-2026-84786: DANE-enabled TLS clients using DANE PKI APIs. Mano Studio's explicit update check uses Python urllib and does not enable DANE.
- CVE-2026-107494 and CVE-2026-84785: OpenSSL QUIC paths. Mano Studio does not create QUIC connections.
- CVE-2026-121482: CMS/PKCS#7 verification with CRL checking enabled. The app does not enable OpenSSL CRL-check flags or process untrusted CMS/PKCS#7 content.

The app uses ordinary HTTPS only for an explicit GitHub release metadata check; it does not use DANE, QUIC, CMS/PKCS#7 verification or CRL checking. This is a source-level reachability assessment, not a vendor-issued exemption or independent penetration test. Keep manual security review open and schedule a rebuild/retest when OpenSSL 3.5.10 is actually published.

The automated review threshold remains 3.5.10, distinct from the latest actually published version (3.5.9). Below-threshold evidence retains advisory-review flags; no dependency pin changes. Synthetic 3.5.10 fixtures test parsing, not availability.
