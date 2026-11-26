# Basic Computer saved examples

Open Computer → Saved examples, choose a program, and confirm replacement. The existing CPU and assembler execute the actual source. Use Step or Run, inspect the memory cells and E, and use Assemble / Reset to repeat. These original examples use the documented named-instruction dialect; they are not copies of textbook pages or saved CPU snapshots.

| Program | Lesson | Steps to halt | Final AC / E | Memory checks (hex addresses) |
|---|---|---:|---|---|
| [Addition](addition.mano) | 5 + 3 | 4 | 0008 / 0 | M[106] = 0008 |
| [Counted loop](counted-loop.mano) | Four additions of 3; ISZ skips when COUNT reaches zero | 14 | 000C / 0 | M[107] = 000C, M[109] = 0000 |
| [Subroutine](subroutine.mano) | BSA stores return address; BUN indirect returns | 6 | 000E / 0 | M[103] = 0101, M[107] = 000E |
| [Indirect](indirect.mano) | Pointer at 103 selects word 200 | 3 | 002A / 0 | M[104] = 002A |
| [Carry](carry.mano) | FFFF + 0001 wraps and sets E | 4 | 0000 / 1 | M[106] = 0000 |

در محیط کامپیوتر، «نمونه‌های ذخیره‌شده» را انتخاب کنید. هر نمونه را گام‌به‌گام اجرا کنید و مقدار ثبات‌های AC و E و حافظه را با جدول بالا مقایسه کنید. این فایل‌ها فقط متن اسمبلی را ذخیره می‌کنند؛ وضعیت زنده پردازنده ذخیره نمی‌شود.

Run `python -m pytest -q tests/test_program_samples.py` to check native files and actual CPU results. Local exact-source result: 14 passed. Qt menu tests are separate.
