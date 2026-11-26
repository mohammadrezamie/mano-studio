# Chapter 1 portable exercises / تمرین‌های فصل اول

These examples use the versioned JSON format and the existing Logic Lab pages. Open the matching page, choose Open exercise, select the file, and confirm replacement. No internet or separate runtime is required. Saving changes produces another portable exercise file. State-machine loading resets the current state and trace; equations and analyses are regenerated, not trusted from a file.

در آزمایشگاه منطق، صفحه مربوط به تمرین را باز کنید و با دکمه «باز کردن تمرین» فایل را انتخاب کنید. پس از تأیید، طرح بارگذاری می‌شود. هنگام بارگذاری ماشین حالت، تاریخچه و حالت جاری بازنشانی می‌شوند و معادلات دوباره محاسبه می‌شوند.

| File | Expected learning outcome |
|---|---|
| karnaugh-corners.mano-exercise.json | Four corner cells (0,2,8,10) form a single wrap-around group; expression B'D'. |
| karnaugh-dont-care.mano-exercise.json | POS example: compare specified output cells and legal X completions. |
| fsm-moore-reduction.mano-exercise.json | Four encoded states, two reachable and equivalent; reduced machine has one abstract state. |
| fsm-mealy-101.mano-exercise.json | Overlapping sequence detector: input 10101 yields pre-edge outputs 00101. Three reachable classes, unused code 3 returns to reset. |

تمرین اول: گروه چهار گوشه و عبارت B'D' را بررسی کنید. تمرین دوم: تکمیل مجاز X و فرم POS را مقایسه کنید. تمرین سوم: حالت‌های معادل و دسترس‌ناپذیر را پیدا کنید. تمرین چهارم: دنباله 10101 را وارد کنید و خروجی 00101 را ببینید.

Format v1: `format=mano-exercise`, `version=1`; `kind=karnaugh` contains values in binary minterm order and SOP/POS; `kind=state-design` contains bits, mode, flipflop and complete rows [next state, output] in Q then X order. Maximum accepted file size 32 KiB; strict validation before replacement. No saved simulation histories, imported signal aliases, or physical netlists. Save physical combinational circuits through existing circuit-document actions instead.

Keyboard / صفحه‌کلید: arrow keys move focus across the visible Karnaugh map; Space cycles the focused value. / کلیدهای جهت‌دار برای حرکت بین سلول‌ها و Space برای تغییر مقدار سلول انتخاب‌شده است.

Developer visual QA: the shipped POS and Moore-reduction files are also used in model-asserted screenshot scenarios for Verify, Analysis and Reduction (both languages, three themes). These are not screenshots of manual acceptance.

## Combinational saved samples
See [Circuit library](CIRCUIT_LIBRARY.md) for six editable JSON circuits and the new block insertion workflow. The [permanent laboratory policy](PRACTICAL_LAB_POLICY.md) extends saved experiments to every applicable textbook section.

Saved combinational circuit files may now also be inserted as blocks with explicit signal mapping; see CIRCUIT_LIBRARY.md.
