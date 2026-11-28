# Qt library replacement review

## Source-modified QtSvg replacement — verified 2026-11-28

The original non-code overlay pilot below is historical. [Run 46102540836](https://github.com/mohammadrezamie/mano-studio/actions/runs/46102540836) successfully compiled QtBase and QtSvg from checksum-verified official 6.12.0 sources using Windows 2022/MSVC. The build appended an explicit exported C++ probe to qsvgrenderer.cpp. The modified DLL was then used on disposable copies of both exact frozen Portable candidates, not the release assets themselves.

Independently downloaded and checked all three evidence ZIPs (SHA-256 and ZIP CRC):

| Evidence | Artifact | SHA-256 |
| --- | --- | --- |
| Build logs, source patch, CMake caches, DLL and exports | 15246658305 | b25bcafcf469080cb896b8c72feacae1d94231e483f01b080480151c24d3211f |
| Stable original/modified/restored smoke | 15246589778 | ad9ff7543b5a60842a364ed8286c08cb3929aae5ebb63c1ab77331a7da7350be |
| Beta original/modified/restored smoke | 15245929298 | 9819654789863c1c30c0030338d1df7053a2948bd4cec1dbe5cc7e1cad975ca3 |

Original Qt6Svg.dll SHA-256: `8f1de5b28aab1eedb415c751c81f9cfaa2804242868c0ceea5f3fdb4b2babca4` in both candidates. Source-modified Qt6Svg.dll (595,968 bytes) SHA-256: `1f453465fa5815c6a799dd25dc9cf874e511c341dfd5bb70f6e9499e51e7ce50`. Both result JSON files match those hashes, the correct exact Portable SHA, and probe return 20261128. All six original/modified/restored reports contain PASS. The build artifact independently matches the modified DLL digest.

The reproducible experimental recipe is in [qt-source-relink-build.yml](../.github/workflows/qt-source-relink-build.yml): build shared QtBase (release, open-source, no tests/examples, no OpenSSL for this pilot), configure/build QtSvg against that prefix, replace only Qt6Svg.dll in a disposable extracted copy, call the exported probe and run application smoke, restore original. The source patch and actual CMake caches are retained in the build artifact. This establishes a genuinely recompiled library replacement for QtSvg on the tested configuration, a stronger result than an appended non-code overlay.

**Scope:** QtSvg only, hosted offscreen smoke, not every LGPL DLL, not independent native desktop acceptance. This is not the official wheel's exact build configuration, not exact corresponding-source proof, not a complete source offer, and not legal or security clearance. Do not distribute the experimental DLL as an update. No frozen release bytes changed.

## Historical overlay pilot

The current Windows onedir portable distributions retain Qt and Shiboken as separate DLL/PYD files under `ManoStudio/_internal/PySide6` and `ManoStudio/_internal/shiboken6`. Candidate archives from build 46041711466 are independently pinned by SHA-256. The experiment tests the original portable application, then a disposable copy with a non-code overlay appended to Qt6Core.dll, then restores the original and repeats smoke. It never edits a public asset or disables OS protection. This is a narrow test of accepting changed DLL bytes at the normal library path, not proof that a genuinely source-modified, ABI-compatible Qt build works, nor legal approval.

For the eventual user-facing instructions: extract a portable copy into a separate user-owned folder, close Mano Studio, retain original files, obtain or build the matching architecture/version/configuration of the LGPL library, and replace its corresponding DLL and required compatible dependencies. Start from the copied application directory and check the desired feature. If it fails, restore the originals. Do not overwrite unrelated files, use untrusted DLLs, bypass OS security policies or edit the installed production copy. Mano Studio's MIT license does not restrict modification of LGPL components or reverse engineering for debugging such modifications. Actual source rebuild commands, matching vendor configuration/patches, third-party notices and durable corresponding-source access still need verification before these instructions are designated final. The historical overlay pilot did not claim source-level replacement or approve redistribution; see the later source-modified QtSvg evidence above.

Latest exact portable archives:
- Stable: bc93823dbea393f17464886abeef406defda22e4151dbaab82293928eae3271e
- Beta: b6a9e2c0fa4014ce505d68e639a328f6ec193b98655c2f123a93365d3b523109
