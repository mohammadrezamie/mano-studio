# Exact OpenSSL replacement handoff

The existing Stable/Beta binaries share both OpenSSL DLL families. This is an internal pilot, not an approved replacement or public release.

## Two builds, one pinned public source

- Official commit: `ee8e3a49f3d9ef5bc8aeaa9eac19e8df236d9dbb`.
- Qt-compatible suffixed pair: [run 46119550008](https://github.com/mohammadrezamie/mano-studio/actions/runs/46119550008).
- Python-compatible unsuffixed pair: [run 46121305189](https://github.com/mohammadrezamie/mano-studio/actions/runs/46121305189).
- Each must independently pass its upstream test suite. Preserve source commit, all 12 fix ancestor checks, configuration dump, license and hashes. Do not label a public source snapshot as an official upstream release.
- The `no-asm` build is an experimental configuration; differences from vendor builds, optional providers and supported CPU capabilities require review.

## Exact baseline and ABI gate

Download the current frozen portable artifacts 15221357225 (Stable) and 15220621215 (Beta). Extract the inner Portable ZIP, not the application directory. Place the four independently built DLLs into one disposable folder, preserving their original filenames. Verify their hashes against the respective build reports.

Run from a Linux host with GNU binutils:
```sh
python scripts/openssl_abi_preflight.py ManoStudio-v1.0.0-Windows-x64.zip replacements/
python scripts/openssl_abi_preflight.py ManoStudio-v1.1.0-beta.1-Windows-x64.zip replacements/
```

On 2026-11-28, the exact Stable baseline was independently examined using the parser's GNU objdump expression. Each original Crypto DLL has 5,872 named exports; each SSL DLL has 603. Both Crypto pairs share their name sets, as do both SSL pairs. The self-comparison passed and a deliberate cross-family SSL substitution was detected as incompatible because libssl-3.dll imports libcrypto-3.dll, while libssl-3-x64.dll imports libcrypto-3-x64.dll. These were parser-level checks against actual baseline files, not tests of the yet-unbuilt replacement DLLs.

## After successful build and ABI preflight

Use disposable candidate copies only. Verify exact source and asset hashes, inspect any additional imported DLLs and OpenSSL provider/configuration requirements, retain both original runtime pairs for rollback, and never rename one family to substitute for the other. Preserve all four library locations. Update the binary inventory and OpenSSL notice/provenance for the actual source build. Recompute installed and Portable hashes and regenerate all package evidence; existing attestations apply only to the original bytes. Test CPython SSL and Qt TLS paths with certificate validation, offline startup, conversion, update failure paths, native graphics, Setup/Portable/upgrade/uninstall. Record any optional-provider or ABI failure rather than suppress it. Final security review must assess actual linked configuration and advisory fixes. Qt source/relink/notice and independent desktop acceptance remain separate gates.

Do not replace the current draft assets until an exact replacement is reviewed and qualified. No automatic installation authorization.
