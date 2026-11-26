"""Offline runnable Basic Computer lessons; expected values are hand-derived."""
from dataclasses import dataclass
from pathlib import Path
import sys
import mano_file


@dataclass(frozen=True)
class Sample:
    key: str
    title: tuple[str, str]
    task: tuple[str, str]
    steps: int
    ac: int
    e: int
    memory: tuple[tuple[int, int], ...]


SAMPLES = (
    Sample("addition", ("Add two words", "جمع دو کلمه"),
           ("Inspect C = 8 after four instructions.", "پس از چهار دستور، مقدار C برابر ۸ است."),
           4, 8, 0, ((0x106, 8),)),
    Sample("counted-loop", ("Counted loop with ISZ", "حلقه شمارشی با ISZ"),
           ("Add 3 four times. ISZ advances -4 to zero and skips the branch.",
            "عدد ۳ را چهار بار جمع کنید. ISZ شمارنده را از منفی ۴ به صفر می‌رساند و از پرش می‌گذرد."),
           14, 12, 0, ((0x107, 12), (0x109, 0))),
    Sample("subroutine", ("Subroutine call and return", "فراخوانی و بازگشت زیرروال"),
           ("BSA stores the return address; indirect BUN returns after doubling 7.",
            "BSA آدرس بازگشت را ذخیره می‌کند؛ BUN غیرمستقیم پس از دوبرابر کردن ۷ بازمی‌گردد."),
           6, 14, 0, ((0x103, 0x101), (0x107, 14))),
    Sample("indirect", ("Indirect memory access", "دسترسی غیرمستقیم حافظه"),
           ("Follow the pointer to 200 and store 42 in RESULT.", "اشاره‌گر را تا 200 دنبال کنید و ۴۲ را در RESULT ذخیره کنید."),
           3, 42, 0, ((0x104, 42),)),
    Sample("carry", ("16-bit addition and carry", "جمع ۱۶ بیتی و نقلی"),
           ("FFFF + 0001 wraps AC to zero and sets E to one.", "جمع FFFF و 0001 انباره را صفر و E را یک می‌کند."),
           4, 0, 1, ((0x106, 0),)),
    Sample("bit-mask", ("Mask the low byte", "ماسک بایت کم‌ارزش"),
           ("AND with 00FF extracts F3 from A5F3. Inspect RESULT.",
            "با AND و ماسک 00FF، بایت F3 از A5F3 جدا می‌شود. RESULT را بررسی کنید."),
           4, 0xF3, 0, ((0x106, 0xF3),)),
    Sample("twos-complement", ("Two's complement negation", "منفی کردن با مکمل دو"),
           ("CMA then INC changes 5 to FFFB (-5).",
            "CMA و سپس INC عدد ۵ را به FFFB (منفی ۵) تبدیل می‌کنند."),
           5, 0xFFFB, 0, ((0x106, 0xFFFB),)),
    Sample("rotate-carry", ("Rotate left through E", "چرخش چپ از طریق E"),
           ("CIL rotates 8001 with E=0 to AC=0002 and E=1.",
            "CIL مقدار 8001 را با E=0 می‌چرخاند؛ AC=0002 و E=1 می‌شود."),
           5, 0x2, 1, ((0x106, 0x2),)),
    Sample("absolute-value", ("Signed absolute value", "قدر مطلق علامت‌دار"),
           ("SPA selects the sign-dependent branch; -7 becomes +7. The minimum signed word 8000 is not representable as a positive 16-bit word.",
            "SPA مسیر وابسته به علامت را انتخاب می‌کند؛ منفی ۷ به مثبت ۷ تبدیل می‌شود. قدر مطلق 8000 در کلمه علامت‌دار ۱۶ بیتی قابل نمایش نیست."),
           7, 0x7, 0, ((0x109, 0x7),)),
    Sample("block-copy", ("Copy three memory words", "کپی سه کلمه حافظه"),
           ("Indirect LDA/STA and ISZ copy 200–202 to 210–212, advancing both pointers and ending with COUNT=0.",
            "LDA و STA غیرمستقیم و ISZ سه کلمه 200 تا 202 را به 210 تا 212 کپی می‌کنند؛ هر دو اشاره‌گر جلو می‌روند و COUNT صفر می‌شود."),
           18, 0xFFFF, 0, ((0x107, 0x203), (0x108, 0x213), (0x109, 0x0), (0x200, 0x1234), (0x201, 0xA5A5), (0x202, 0xFFFF), (0x210, 0x1234), (0x211, 0xA5A5), (0x212, 0xFFFF),)),
)


def load_sample(key, root=None):
    sample = next((item for item in SAMPLES if item.key == key), None)
    if sample is None:
        raise ValueError("Unknown program sample")
    base = Path(root) if root is not None else Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    kind, source = mano_file.load(base / "examples" / "programs" / (sample.key + ".mano"))
    if kind != "asm" or not source.strip():
        raise ValueError("Invalid saved assembly sample")
    return sample, source
