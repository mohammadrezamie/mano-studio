# OpenSSL 3.5.9 notice evidence

Independent inspection of both exact portable payloads (artifact IDs 15180064025 and 15198955230) found identical four SSL/crypto DLLs. Both libcrypto binaries embed 3.5.9; the two libssl binaries contain no recognized version string. The Python license present in both packages is 35,407 decoded characters and does not contain the term OpenSSL. No standalone OpenSSL license file was present. The upstream 3.5.9 LICENSE.txt is retained unmodified here (Git blob 49cc83d2ee29d13453188217f0e4edd70c7f842f, upstream tag object d0ca66a1abe52545f14eca635c648932fcde5615), not a substitute for complete third-party notices, exact DLL provenance or a patched build. Source: https://github.com/openssl/openssl/blob/openssl-3.5.9/LICENSE.txt . Both crypto files need provenance tied to the supplying distribution and corresponding notices. Manual public releases must carry applicable licenses; no automatic install or security clearance is inferred from this text. No modification to frozen archives.


## 2026-11-28 advisory review — both frozen candidates

The earlier paragraph describes superseded artifacts; refreshed exact candidates 15221357225 and 15220621215 contain the OpenSSL license. Official downloads still list 3.5.9 as the published 3.5 LTS patch. The official 3.5 advisory table lists twelve low-severity entries dated 10, 17 and 24 November with affected range through 3.5.9. This extends the four-entry 24 November review on release/stable-qt-notices; the three runtime preflight flags are not a count of CVEs.

| IDs (CVE-2026-) | Feature needed for exposure | Candidate assessment |
| --- | --- | --- |
| 84785, 107494, 124709, 88822, 95691 | QUIC streams, peer detection or handshake | Ordinary HTTPS updater; no known application QUIC path |
| 121482, 107496 | CMS/PKCS7 CRL verification or CMS encryption | No known application CMS processing |
| 84786 | DANE-enabled TLS | No known DANE enablement |
| 107493 | Caller-supplied PEM info stack reused after failed load | Ordinary TLS CA loading uses the safe null-stack path per upstream; other callers not fully audited |
| 35190 | TLS server with non-default Suite B certificate flag | No known application TLS server |
| 88823, 95692 | Explicit AES-GCM-SIV operations with affected input | No known application use of that cipher API |

Sources checked 2026-11-28: https://www.openssl-library.org/news/vulnerabilities-3.5/ and https://www.openssl-library.org/source/ . This is an applicability triage, not a proof of unreachable code across Python/Qt native dependencies. The existing exact-byte scan supports absence of explicit application DANE/QUIC/CMS paths, but additional native-library reachability and security review remain open. No synthetic 3.5.10 pin or claim that an unpublished release is available. New no-Mesa review packages use the same application binaries and therefore do not clear these flags. Do not wait for unrelated forward features; determine security disposition on the actual distribution before promotion.
