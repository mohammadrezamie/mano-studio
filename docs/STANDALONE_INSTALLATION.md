# Standalone Windows installation — permanent owner policy

Owner requirement, 2026-11-26. Both Stable (#4) and Beta (#23) must be easy to install: a user downloads Setup, runs it and opens Mano Studio. No separate prerequisite installation or internet connection for installation and core operation.

- Package compatible private Python, Qt and app libraries alongside the application. Do not install Python/Qt globally, alter PATH or overwrite a user's existing environment. Private files may duplicate an existing system version deliberately for isolation; this is not a second system-wide installation.
- Prefer compatible existing shared system prerequisites when genuinely needed. Do not reinstall an already sufficient shared runtime. Never blindly replace an incompatible global runtime; prefer authorized app-local deployment where supported, and resolve missing requirements within Setup without burdening users. If future shared prerequisite bootstrap is unavoidable, verify official signed redistributable, architecture, version detection and license, and handle restart/failure explicitly. No new redistributable bootstrap is implemented in this checkpoint.
- Keep per-user installation and uninstall scoped to our app; leave other applications and shared runtimes intact. No automatic downloads or startup network checks.
- Keep the portable version usable after extraction. Developer source checkout may require Python and pip, but the packaged application must not.

## Acceptance matrix
| Machine | Required observation |
|---|---|
| Clean supported Windows 10/11 x64, no developer tools, offline | One Setup; successful launch, translation, example, simulator, export; no manual prerequisites |
| Existing compatible Python/Qt/shared runtimes | Same app behavior; no global reinstall, no PATH changes, other apps unaffected |
| Existing incompatible developer environment | Private app modules load from install directory; system environment unchanged |
| Reinstall/upgrade/uninstall | No unrelated runtime removal; preserve user settings/documents; no unnecessary downloads |

Record OS, user privilege, exact Setup hash/source SHA, actual loaded DLLs and observed results. Test native Windows on clean and pre-equipped machines separately. A hosted runner is not a clean VM.

## Implementation checkpoint
Current installer already copies a frozen PyInstaller directory and has no prerequisite installer or global PATH change. New installed smoke temporarily restricts process PATH and removes developer Python/Qt environment overrides, launches from the installation directory, then restores the runner environment. Runtime probe records actually loaded private Python/Qt/SSL paths, requires them under the install root, records shared C runtime locations without changing them, and creates a TLS context without network access. No source translator modification. Probe and Windows run not yet verified; clean VM, upgrade, and redistribution/security clearance remain release gates. The diagnostic is not a guarantee that every optional module or DLL is isolated.
