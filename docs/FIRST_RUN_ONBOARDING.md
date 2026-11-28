# First-run onboarding — first implementation increment

Independent next-generation branch, not part of either frozen release candidate. A real startup splash retains academic thanks; a new profile sees a six-page bilingual wizard (language selection, welcome, RTL, Basic Computer, Logic, Learning Center). Navigation and language selection resume locally; completion persists language and opens the actual application. Existing profiles bypass the wizard. No artificial delay, network, or translator changes.

The versioned settings state is standard-library only and is covered separately from the Qt dialog. The launcher retains splash behavior before and after the first-run wizard. Explicit close saves progress and exits; subsequent launch resumes. Current pages introduce workspaces with text and existing brand mark, not a screenshot-based or spotlight tour yet. Settings language migration, licensed font bundling, actual visual screenshots and overlay coach marks remain follow-up work under #56. Verify platform behavior and integration before acceptance.

## Settings and typography increment

Visible header language selector removed; Settings offers an explicit Apply language control, updates the current workspace without replacing documents, and reopens the dialog in the selected language. Active update operations prevent language changes. Internal hidden compatibility selector retained for existing CI/capture scripts. Completed onboarding language is synchronized; unknown state schema is preserved. Reuse the exact accepted candidate's platform-aware offline font selection (Vazirmatn/Noto Sans Arabic/Tahoma and Segoe UI/Inter/Noto Sans when available). Code editor font and LTR direction remain independent. No font files bundled yet. Focused state/UI tests added; acceptance pending.

## Spotlight tour increment

A reusable child overlay highlights ten actual controls in the translator workspace with bilingual coach marks, Next/Back/Skip/Finish, Escape and keyboard focus cycling. It avoids edits and blocks underlying workspace inputs/shortcuts while active; tracks target geometry on root resize/layout, skips hidden targets, saves completion/skip, and replays via Help. Fresh completed onboarding records a pending tour; opening a file explicitly takes precedence. Legacy profiles are not forced into a tour. This increment introduces other labs through the existing Learning Center entry rather than walking inside every separate lab dialog. Native visuals, small-window placement and cross-lab guided routes require further acceptance. No frozen candidate changes.
