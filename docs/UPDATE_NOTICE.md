# Optional update notification — beta track

Off by default; explicit opt-in in Settings. Bounded asynchronous HTTPS metadata request to the fixed GitHub API after the workspace appears; no redirects, no automatic downloads, no installer launch, no telemetry. Same channel parser as manual updates. A persistent status-bar button opens Settings; first notice per tag also appears in the status bar. Cancellation on opt-out or close. Qt network TLS behavior and packaged runtime compatibility require verification on Windows; tests added for default offline, consent, channel filtering, response size, and bilingual notice. Native update installation and publisher trust remain unresolved. No modification to either frozen release candidate.


## Explicit download behavior

When GitHub metadata identifies exactly one Windows x64 Setup asset with a valid expected size and SHA-256 digest, Settings enables the Download installer action. The user confirms the download and chooses the destination. The worker downloads to a temporary file, checks the exact size and SHA-256, and only then publishes the file without overwriting an existing destination. SHA-256 is integrity, not publisher authentication. The application does not execute or install the downloaded EXE; the user must independently verify the publisher before running it. Missing/ambiguous digest metadata leaves the download action disabled. Automatic installer launch remains fail-closed pending trusted publisher identity and end-to-end upgrade acceptance.
