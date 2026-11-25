# Documentation policy — living README

Owner decision, 2026-11-25. The README is the current entry point, not a one-time marketing document. This rule applies permanently to both Release and Next-generation tracks.

## Definition of done

Every meaningful change must update README.md and the affected documentation in the same work cycle, preferably the same PR/commit series. Record feature additions/removals, routes, UX, dependencies, compatibility, academic rules, known limitations, tests, packaging, release state, and roadmap changes. For an internal change that does not affect user-facing claims, update the status/handoff and explicitly record why the README needs no content change. Do not postpone a material README change until release.

- Before work: inspect live main, active release/feature heads, README and relevant docs.
- During work: keep the branch's feature/status descriptions accurate; label draft or unverified features.
- After work: reconcile README, STATUS, CONTINUE, affected guides, curriculum and issue/PR evidence. Verify relative links and asset paths at the actual branch.
- Before merge: reconcile concurrent documentation edits and distinguish the merged baseline from candidate and future features. Never restart active release CI simply to change marketing copy; use isolated docs updates and merge at a safe checkpoint.

## Evidence and visuals

Use English as the primary documentation language. Preserve concise Persian guidance where it materially helps the academic assignment; do not generate Persian text inside images. Use the approved M-chip vector, restrained badges and a small number of real, representative screenshots. The local documentation logo is a static rendition of candidate ui/brand.py (dark glass, neutral, no animation); record provenance and refresh it when geometry changes. Do not present generated concepts as screenshots, fabricate official seals or endorsements, or link nonexistent images. Link verified artifact runs when screenshots are not bundled. Use accessible alt text and relative paths for local assets.

Every numerical or release claim must name the relevant commit/run, and pending tests must remain pending. CI screenshots are not native acceptance. Distinguish indexed chapters from complete textbook coverage, source merges from public releases, and the standalone academic translator from optional labs.

## Review checklist

- [ ] README reflects the meaningful changes, or a documented no-impact rationale exists.
- [ ] Release and next-generation states are clearly separated.
- [ ] Installation/CLI commands, links and local assets match actual files.
- [ ] STATUS, CONTINUE, affected guides and issue/PR evidence agree.
- [ ] Unverified features, limitations and tests are explicitly labeled.
- [ ] English-first presentation, minimal images, truthful captions and readable Persian guidance.
- [ ] Standalone translator contract and offline behavior are preserved.

This policy requires human/agent review; it does not claim that an automatic documentation freshness check is installed.
