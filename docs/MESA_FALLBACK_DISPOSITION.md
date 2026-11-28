# Mesa software renderer — exact candidate disposition

2026-11-28. The two exact portable packages contain the same 20,639,544-byte opengl32sw.dll (SHA-256 18aedc7a4b610f53bcc7b7a5c5ed9293c7e86f030e3273ad54ed3bb1ebd36702), identifying Mesa 11.2.2 and LLVM 3.6.2 in string inspection. Existing third-party notice inventory did not identify Mesa attribution. This is a notice/provenance gap, not a demonstrated exploit.

## Verified external references

- Qt's [official binary archive index](https://download.qt.io/development_releases/prebuilt/llvmpipe/windows/) lists x64 Mesa 11.2.2 variants, including the SHA-256-signed archive dated 2022-11-29.
- Qt's [published checksums](https://download.qt.io/development_releases/prebuilt/llvmpipe/windows/sha256sums.txt) pin `opengl32sw-64-mesa_11_2_2-signed_sha256.7z` to `c61f801c1760aa24b02c7a8354323cddf368b86f8f5c34b50b3b224f7d728afd`. This is the outer 7z hash, not the inner DLL hash. Direct retrieval in the current assistant container failed; byte matching of this specific vendor archive remains unverified.
- [Qt's Mesa build wiki](https://wiki.qt.io/MesaLlvmpipe) documents patched builds and identifies the older Mesa 11.2.2/LLVM 3.6 combination. The current recipe shown is for a newer version; it does not prove the exact historical patch set.
- [Qt 6.5 Mesa attribution](https://doc.qt.io/qt-6.5/qt-attribution-llvmpipe.html) identifies MIT and Boost Software License 1.0 and the associated Brian Paul, Khronos and C11 emulation notices. This is upstream attribution evidence, not an exhaustive legal inventory of the embedded LLVM components.
- [Qt 6.12 deployment guidance](https://doc.qt.io/qt-6.12/windows-deployment.html) identifies the software OpenGL renderer; [Qt 6.12 namespace documentation](https://doc.qt.io/qt-6/qt.html) explains the patched software fallback. Removal has a compatibility cost on systems needing software rendering.

## Decision

Hosted original/no-Mesa smoke passed on both exact portable copies with Windows and offscreen QPA plugins in run 46103799520, artifacts 15245878703 and 15246845503. This is not independent physical/VM GPU coverage or a complete feature test. Do not declare software rendering unnecessary for every supported system.

Forward PRs #75 and #76 add guarded optional exclusion only. Current initial release drafts remain unchanged. The release owner needs a reviewed disposition: retain the fallback with correct complete notices and reviewed dependency risk, or exclude it in newly identified candidates and validate compatibility including the expected behavior on hardware without usable OpenGL. No need to repeat unrelated tests for the existing frozen hashes; a changed package must have its own acceptance and attestation.

Qt LGPL obligations for other shipped libraries remain distinct: [official guidance](https://www.qt.io/development/open-source-lgpl-obligations) calls for corresponding library source, applicable notices and the ability to run modified/relinked software. Neither the Mesa pilot nor a passing source-relink experiment establishes legal approval. Do not claim an independent legal review happened.

## Actual vendor archive comparison — 2026-11-28

[Run 46104288484](https://github.com/mohammadrezamie/mano-studio/actions/runs/46104288484) downloaded the official signed-SHA256 7z archive, matched its published outer digest and extracted one DLL. Vendor DLL SHA256 `b04de4541863bc7d8879040a78889c4849c1b1da2784c4630f734c146c2998ce`, 20,639,888 bytes, differs from the frozen DLL by 344 bytes in total file size. The job correctly failed the exact-byte identity gate. A size difference alone cannot establish that only certificate data differs. Artifact 15247045744 holds the negative result. Do not claim the signed archive as the exact shipped binary. Compare other vendor archive variants or PE sections/signature separately, not the public package. The successful no-Mesa pilot remains valid.
