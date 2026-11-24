# UI/UX Pro Max — vendored third-party design skill

- **Upstream repository**: https://github.com/nextlevelbuilder/ui-ux-pro-max-skill
- **Pinned source commit**: `2de1134dc4d1cfe112934611ae5803ae17a1bd7e`
- **License**: MIT; retain the `LICENSE` file in this folder. Original authors retain credit.
- **Location**: `.agents/skills/ui-ux-pro-max/`, usable by any compatible agent that reads repo skills; Claude Code bridge at `.claude/skills/ui-ux-pro-max/SKILL.md`.
- **Actual runtime copied**: 47 upstream skill/data/reference/script files, 22 stack CSVs, original multi-domain Python offline search and design system generation. Omitted upstream Python test fixtures and the upstream `phosphor-icons-upstream.json` source snapshot (actual runtime search uses `icons.csv`); no npm/composer dependency introduced.
- **Adaptation**: replaced upstream `CLAUDE_PLUGIN_ROOT` script paths with Git-root-relative `.agents/skills/ui-ux-pro-max` references, inserted a TNA governance warning, and removed whitespace from 46 blank lines in `scripts/design_system.py` to pass Quality’s whitespace check. Do not override `AGENTS.md`, brand-specific art direction, approved UX, permissions, privacy or frozen parent-company root.
- **Runtime prerequisites**: Python 3 standard library. Verify in real checkout:
  ```bash
  python3 .agents/skills/ui-ux-pro-max/scripts/search.py "robotics premium interface" --stack laravel
  python3 .agents/skills/ui-ux-pro-max/scripts/search.py "robotics industrial design" --design-system -p "TakinPro"
  python3 .agents/skills/ui-ux-pro-max/scripts/search.py "Persian high-contrast dark mode" --domain ux
  ```
- **Design suggestions are not approved design direction**. Before use, verify real font license, Persian glyph shaping, FA/EN bidi, WCAG, performance and current library/version compatibility.
- **Update policy**: verify upstream change and license/safety, run local smoke tests, then update in a focused PR. No automatic upstream download or unpinned runtime execution.
