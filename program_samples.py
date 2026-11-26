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
