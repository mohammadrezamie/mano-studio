# Chapter 7 microprogram workbench

This is a distinct educational computer, not the Chapter 5 Basic Computer or the academic RTL translator.

Select Raw HEX or Symbolic microassembly, then Load / Reset. A mode switch invalidates the loaded image without erasing source; Example explicitly loads a matching example. Data memory remains sparse hexadecimal address:word. Initial CAR is decimal (64 default). Control listing is hexadecimal address:20-bit word.

Symbolic grammar (case insensitive):

- ORG decimal-address (0–127); explicit 0x hex allowed.
- Optional label: before an operation, or on a line by itself.
- One or more comma-separated microoperations, then condition U/I/S/Z, branch JMP/CALL/RET/MAP, and target.
- JMP/CALL require a decimal/0x address, label or NEXT (CAR+1 modulo 128).
- RET/MAP omit target or use zero. Comments begin with # or semicolon.
- NOP must stand alone. Multiple operations in one F group, duplicate register destinations, READ/WRITE overlap, reserved operations, duplicate addresses, unknown labels and out-of-range addresses are errors.
- Two passes resolve forward labels; any error prevents loading any control words. Numeric destinations may refer to empty control addresses; execution then explicitly stops with an uninitialized-address error. SBR is a single return register, not a stack.

Example (a short standalone control program):
```
ORG 64
BEGIN: CLRAC U JMP NEXT
INCAC U JMP BEGIN
```

The built-in symbolic example implements the four Chapter 7 sample machine opcodes ADD, negative conditional BRANCH, STORE and EXCHANGE, shared indirect address subroutine and fetch/mapping. It is a small original educational memory image and is not a complete 16-opcode ISA.

Persian: برای نوشتن ریزبرنامه حالت نمادین را انتخاب کنید. دستور ORG آدرس ده‌دهی حافظه کنترل را تعیین می‌کند. برچسب‌ها می‌توانند به جلو ارجاع دهند. در صورت خطا هیچ تصویر ناقصی بارگذاری نمی‌شود. مدل فصل هفتم مستقل از فایل تکلیف اصلی است.

Reference: Mano, Computer System Architecture, 3rd edition, chapter 7; lecture slides by Alon Schclar, https://www.carmimerimovich.net/teaching/history/2020-1/2020-1S-Architecture/chap07.pdf . Implementation written independently.
