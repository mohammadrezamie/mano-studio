# Direction-aware input and startup UX

Owner requirements (2026-11-27): preserve the Photoshop-style real startup splash with academic thanks, and provide a reusable specialized keyboard in both translation directions. The current code already has QSplashScreen, bilingual credits in ui/credits.py, a canonical reverse converter, and an instruction builder for both directions. Previously the Symbol pad was disabled in reverse mode.

This increment keeps both keypad layouts in a single editor tab. RTL has registers, arrow, logical operators, memory brackets, conditional syntax and hexadecimal digits. Assembly has all 25 named instructions from instruction_catalog.TEMPLATES, optional indirect marker I, hex digits and comment marker. Shared space, enter, backspace, cursor, undo and redo controls. Technical keys remain LTR in Persian. Reverse input is canonical named instructions, not arbitrary assembler labels, directives or original RTL reconstruction. No changes to rtl_translator.py.

Further work: shared keypad in other assembly editors (Computer lab and any supported code-input view), keyboard accessibility and adaptive layout review, staged real startup progress, font/credit clipping across themes and DPI, first-run setup and guided tour (#56). Reuse credits.py and avoid artificial startup delay. Preserve both frozen release candidates. Test and visual evidence pending.
