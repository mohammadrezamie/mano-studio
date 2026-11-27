# Reduce unnecessary Qt runtime dependencies

Independent local inspection of exact portable archive SHA-256 values confirmed both candidates contain 111 PE binaries (DLL/PYD/EXE). GNU objdump -p successfully parsed every binary. Ordinary PE imports from outside the five-member QML/Quick group into that group: none. No QtQml/QtQuick Python binding was found. Internal dependencies: Qt6Quick -> QmlMeta, QmlModels, Qml; QmlMeta -> QmlModels, QmlWorkerScript, Qml; QmlModels and QmlWorkerScript -> Qml. These same five DLLs total 13,403,160 bytes in each candidate. Normal import inspection is not proof against dynamic loading or feature regressions.

New Windows pilot compares original portable smoke against a disposable copy with only these five DLLs removed. Never changes an original candidate, installer or release asset. Passing smoke is only initial evidence; full frozen application, all features, native visuals, dynamic dependencies and independent packaging acceptance are required before a lean candidate can be promoted. QtBase/Svg and PySide/Shiboken licensing obligations remain; QtPdf present only in Beta, and OpenSSL remains.

Current review: Qt CVE-2026-123706 affects VectorImage, a Qt Quick component; ordinary import evidence supports evaluating removal rather than assuming safe merely because UI uses widgets. Qt Network HTTP advisory CVE-2026-116337 concerns HTTP resource exhaustion, and original candidates' updater uses Python urllib, not proof of nonreachability through other code. OpenSSL native _ssl/_hashlib imports were confirmed; both libssl/libcrypto name pairs remain, so do not remove them arbitrarily. No security approval claimed.

References:
- https://www.qt.io/blog/security-advisory-cve-2026-123706-qt
- https://www.qt.io/blog/security-issue-cve-2026-116337
- https://www.qt.io/development/open-source-lgpl-obligations
- https://openwall.com/lists/oss-security/2026/11/10/12
