# Exact remediated candidate handoff — 2026-11-28

Review only. Both public releases remain drafts. Do not publish older draft assets or treat hosted tests as independent native acceptance.

| Track | Exact source | Windows artifact | Setup SHA-256 | Portable SHA-256 |
| --- | --- | --- | --- | --- |
| Stable 1.0.0 | 926272ff0ebfa4731cfb0b00c149c7e12b4d5a56 | [15255712859](https://github.com/mohammadrezamie/mano-studio/actions/runs/46125406201/artifacts/15255712859) | c80946e956e2d9384fab629c5f6bb4ac648d65d6cb987ab4e49cc9cc944e7ce9 | 5fa7c3f2e79290126c2cd7e401f60652f5dfb5ba82a48af3d69f551e533fa0c3 |
| Beta 1.1.0-beta.1 | 2dd55994d36f2596dd3d17ea54dd3c3e43829ae2 | [15266171804](https://github.com/mohammadrezamie/mano-studio/actions/runs/46151649796/artifacts/15266171804) | 5a125ba3e41d49025954e4284c17c620d94663f7911f2ae3ca1165149d30ea29 | 244f9c6e72cc13ddac3e28047bf688ff652e8f0aec31e084b6304cab146e5f9b |

## Consolidated source evidence

[Artifact 15266261863](https://github.com/mohammadrezamie/mano-studio/actions/runs/46152196473/artifacts/15266261863), 169,592,810 bytes, SHA-256 `574c0e081102ec6a0aa688d71aebcf294aaff4ebb3750df4f947a3c59aec52a5`. Independently downloaded and checked outer digest, ZIP CRC, and all 63 SHA256SUMS entries; exact membership (64 regular files including SHA256SUMS). Contains seven Qt/PySide source tar.xz archives and exact OpenSSL commit tar.gz, configuration and source/build reports. This establishes preserved evidence, not full corresponding-source determination. The Actions artifact expires; a durable public source delivery location must be established before public distribution.

## Remaining decisions

- Exact Qt vendor build correspondence and complete applicable notices/source/relink obligations: independent review pending.
- OpenSSL fixes: both source build test suites PASS, both remediated packages passed hosted DLL context and install smoke; review of exact runtime security disposition and full TLS behavior remains. The 3.5.10-dev snapshot is not an official release.
- Native Windows acceptance: independent execution on clean standard-user and pre-equipped environments, including graphics fallback after Mesa removal, offline RTL conversion, bilingual persistence, setup and portable. Record exact hashes and observed results. Beta lacks the Stable runtime-probe command; do not mark this diagnostic as passed.
- Replace draft assets with exact approved bytes, corresponding-source delivery, checksums and disclosures only after the above. Existing drafts refer to older bytes. The connected GitHub interface does not expose release upload/publish or workflow dispatch actions; authorized manual release operation or a separately reviewed workflow is needed.

No additional packaging job is needed merely to verify these hashes.
