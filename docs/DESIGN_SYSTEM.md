# Mano Studio design system
Owner direction: a modern minimal desktop product rather than a dated industrial simulator. Preserve scientifically recognizable schematic symbols, not the look of legacy tools.

## Implemented foundation
- Single Qt palette and stylesheet in ui/theme.py, Light/Dark/Night. Opaque editors, restrained simulated glass shell, plain fallback.
- Spacing scale 4/8/12/16/24/32 logical px; control/panel/shell radii 9/14/16; type roles caption/body/section/title/hero. Use existing system font and original SVG icons. Only adopt tokens as layouts are touched; no blanket rewrite.
- Learning Center: concise chapter/route summary, searchable list, prominent task, subdued remaining-gap text, focus-visible controls and personal progress. Maintain Persian RTL and technical LTR.
- Shared MotionTabs and application-wide reduced-motion policy; see ANIMATION_GUIDE.md.

## Acceptance and remaining work
Every new page must preserve primary task hierarchy, keyboard navigation, three themes and bilingual text. Text-token contrast is tested mathematically; actual widget states, high DPI, screen reader support, 100%/150% scaling, small windows and Windows visual quality still require real review. Keep glass effects optional. No claim of native Windows Mica or Apple Liquid Glass. Reuse existing components; future Qt Quick experiments must replace, never duplicate, a surface.



## Design system and motion checkpoint
Owner reaffirmed full Morris Mano coverage, exceptional modern minimal appearance, restrained purposeful animation, clean integration, modern technology and continuous documentation. Kept established PySide6/Qt 6 Widgets and shared scientific engines; no parallel shell or new dependency. Added shared spacing/radius/type tokens, improved learning center hierarchy and focus/list/progress styles, and lightweight 160 ms tab-indicator motion across editor, Computer, Logic and nested inspectors. Global reduced-motion preference snaps active indicators immediately; hidden/resized tabs snap, no idle animation or text/circuit opacity. Authored contrast-token, plain fallback, motion policy and UI role tests. Exact prior Learning Center head adbe584 passed both runs 45470016045 and 45470000518. Latest CI and native visual verification pending. Qt Quick is a selective future option, not implemented or required; see DESIGN_SYSTEM and TECH_STACK. No translator, installer or release changes.
