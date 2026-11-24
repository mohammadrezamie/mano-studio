"""Offline examples for the documented instruction-level RTL dialect."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Example:
    key: str
    title: tuple[str, str]
    description: tuple[str, str]
    rtl: str
    data: tuple[tuple[int, int], ...] = ()


EXAMPLES = (
    Example("addition", ("Add two memory words", "جمع دو کلمه حافظه"),
            ("Load 5 and add 3; store the result at 102.",
             "مقدار ۵ را بارگذاری و با ۳ جمع کنید؛ نتیجه در 102 ذخیره می‌شود."),
            "AC ← M[100]\nAC ← AC + M[101]\nM[102] ← AC\nS ← 0\n",
            ((0x100, 5), (0x101, 3))),
    Example("registers", ("Register operations", "عملیات ثبات‌ها"),
            ("Clear AC, increment, complement and halt.",
             "انباره را صفر، افزایش و متمم کرده و اجرا را متوقف کنید."),
            "AC ← 0\nAC ← AC + 1\nAC ← ¬AC\nS ← 0\n"),
    Example("indirect", ("Indirect addressing", "آدرس‌دهی غیرمستقیم"),
            ("Location 100 points to 200, which contains 42.",
             "خانه 100 به خانه 200 اشاره دارد که مقدار ۴۲ در آن است."),
            "AC ← M[M[100]]\nM[101] ← AC\nS ← 0\n",
            ((0x100, 0x200), (0x200, 42))),
    Example("conditional", ("Conditional skip", "پرش شرطی"),
            ("When AC is zero, skip increment and halt.",
             "وقتی AC صفر است، دستور افزایش اجرا نمی‌شود."),
            "AC ← 0\nIF AC = 0 THEN PC ← PC + 1\nAC ← AC + 1\nS ← 0\n"),
)


def computer_source(example, assembly):
    """Add example data only to the optional simulator, never to exported ASM."""
    if not example.data:
        return assembly
    records = [assembly]
    for address, value in example.data:
        records.extend((f"ORG {address:03X}", f"HEX {value:04X}"))
    return "\n".join(records) + "\nEND"
