"""Bilingual data-code conversion and single-error-correction teaching view."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget,QVBoxLayout,QComboBox,QLineEdit,QLabel,QPlainTextEdit
from data_codes import bcd_encode,bcd_decode,binary_to_gray,gray_to_binary,ascii_encode,ascii_decode,hamming_encode,hamming_decode

MODES=(
    ("BCD encode","رمزگذاری BCD",bcd_encode,"123"),
    ("BCD decode","رمزگشایی BCD",bcd_decode,"0001 0010 0011"),
    ("Binary → Gray","دودویی به گری",binary_to_gray,"1011"),
    ("Gray → Binary","گری به دودویی",gray_to_binary,"1110"),
    ("ASCII encode (7-bit)","رمزگذاری ASCII هفت‌بیتی",ascii_encode,"Mano"),
    ("ASCII decode (7-bit)","رمزگشایی ASCII هفت‌بیتی",ascii_decode,"1000001"),
    ("Hamming (7,4) encode","رمزگذاری همینگ (۷،۴)",hamming_encode,"1011"),
    ("Hamming (7,4) decode","رمزگشایی همینگ (۷،۴)",hamming_decode,"0110011"),
)

class DataCodesView(QWidget):
    def __init__(self,fa=False):
        super().__init__()
        self.fa=fa
        layout=QVBoxLayout(self)
        self.mode=QComboBox()
        for en,fa_name,fn,example in MODES:self.mode.addItem(fa_name if fa else en)
        layout.addWidget(self.mode)
        self.note=QLabel()
        self.note.setWordWrap(True)
        layout.addWidget(self.note)
        self.input=QLineEdit()
        self.input.setMaxLength(256)
        self.input.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.input.setAccessibleName(self.t("Input code","کد ورودی"))
        layout.addWidget(self.input)
        self.output=QPlainTextEdit()
        self.output.setReadOnly(True)
        self.output.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.output.setAccessibleName(self.t("Encoded or decoded result","نتیجه تبدیل کد"))
        layout.addWidget(self.output,1)
        self.status=QLabel()
        self.status.setWordWrap(True)
        self.status.setProperty("state","error")
        layout.addWidget(self.status)
        self.mode.currentIndexChanged.connect(self.load)
        self.input.textChanged.connect(self.refresh)
        self.load()
    def t(self,en,fa):return fa if self.fa else en
    def load(self,*_):
        index=self.mode.currentIndex()
        descriptions=[
            self.t("8421 BCD: four bits per decimal digit; leading zeros preserved.","BCD وزن‌دار ۸۴۲۱: چهار بیت برای هر رقم ده‌دهی؛ صفرهای ابتدایی حفظ می‌شوند."),
            self.t("Each four-bit group must represent 0–9.","هر گروه چهاربیتی باید عدد ۰ تا ۹ باشد."),
            "G = B XOR (B >> 1)",
            self.t("Binary bits are the cumulative XOR of Gray bits from MSB.","بیت‌های دودویی حاصل XOR تجمعی بیت‌های گری از سمت پرارزش هستند."),
            self.t("Standard 7-bit ASCII, not UTF-8 or extended ASCII.","ASCII استاندارد هفت‌بیتی، نه UTF-8 یا ASCII توسعه‌یافته."),
            self.t("Control characters are displayed with escaped notation.","نویسه‌های کنترلی با نماد گریز نمایش داده می‌شوند."),
            self.t("Even parity; positions 1, 2, 4 are parity bits; data at 3, 5, 6, 7 (left to right).","زوجیت زوج؛ موقعیت‌های ۱،۲،۴ بیت توازن و ۳،۵،۶،۷ داده هستند (از چپ به راست)."),
            self.t("Assumes at most one erroneous bit. Multiple errors may be miscorrected; not SECDED.","حداکثر یک بیت خطادار فرض می‌شود. خطاهای چندبیتی ممکن است اشتباه تصحیح شوند؛ SECDED نیست."),
        ]
        self.note.setText(descriptions[index])
        self.input.setText(MODES[index][3])
        self.refresh()
    def refresh(self,*_):
        self.output.clear()
        self.status.clear()
        index=self.mode.currentIndex()
        try:
            value=MODES[index][2](self.input.text())
        except ValueError as exc:
            self.status.setText(self.t(str(exc),"ورودی برای کد انتخاب‌شده نامعتبر است؛ قالب و طول آن را بررسی کنید."))
            return
        if index==7:
            value=self.t("Syndrome: ","نشانگان خطا: ")+str(value.syndrome)+"\n"+self.t("Corrected code: ","کد تصحیح‌شده: ")+value.corrected+"\n"+self.t("Data: ","داده: ")+value.data
        elif index==5:
            value="".join(c if 32<=ord(c)<127 else f"\\x{ord(c):02X}" for c in value)
        self.output.setPlainText(value)
