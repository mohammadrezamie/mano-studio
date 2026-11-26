"""Independent event-by-event latch and asynchronous-control inspector."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QWidget,QVBoxLayout,QHBoxLayout,QLabel,QComboBox,
    QCheckBox,QPushButton,QTableWidget,QTableWidgetItem,QHeaderView,QAbstractItemView)
from storage_elements import PINS,Storage,step


TITLES={
    "SR_NOR":("SR latch · NOR (active high)","لچ SR · NOR (فعال با یک)"),
    "SR_NAND":("SR latch · NAND (active low)","لچ SR · NAND (فعال با صفر)"),
    "D_LATCH":("D latch · level sensitive","لچ D · حساس به سطح"),
    "D_ASYNC":("D flip-flop · asynchronous controls","فلیپ‌فلاپ D · کنترل ناهمگام"),
}
NOTES={
    "SR_NOR":("S=R=1 forces both outputs low. Simultaneous release leaves the state unknown.",
        "S=R=1 هر دو خروجی را صفر می‌کند. رهاسازی هم‌زمان، حالت را نامعلوم می‌گذارد."),
    "SR_NAND":("Sbar=Rbar=0 forces both outputs high. Simultaneous release is unknown.",
        "Sbar=Rbar=0 هر دو خروجی را یک می‌کند. رهاسازی هم‌زمان نامعلوم است."),
    "D_LATCH":("EN=1 is transparent; EN=0 retains the previous state without an edge.",
        "در EN=1 لچ شفاف است؛ EN=0 حالت قبلی را بدون نیاز به لبه نگه می‌دارد."),
    "D_ASYNC":("Active-low PREbar/CLRbar override the clock; both asserted means unknown. Otherwise D is sampled at a rising edge.",
        "ورودی‌های فعال با صفر PREbar/CLRbar بر ساعت اولویت دارند؛ فعال بودن هر دو حالت نامعلوم است. در غیر این صورت D در لبه بالارونده نمونه‌برداری می‌شود."),
}


class StorageView(QWidget):
    def __init__(self,fa=False):
        super().__init__()
        self.fa=fa
        box=QVBoxLayout(self)
        self.selector=QComboBox()
        self.selector.setAccessibleName(self.t("Storage element","عنصر حافظه"))
        for kind,title in TITLES.items():
            self.selector.addItem(title[fa],kind)
        box.addWidget(self.selector)
        self.note=QLabel()
        self.note.setWordWrap(True)
        box.addWidget(self.note)
        prompt=QLabel(self.t("Set inputs, then apply one simultaneous event. The live clocked model is unchanged; this is not a physical race simulation.",
            "ورودی‌ها را تنظیم و یک رویداد هم‌زمان اعمال کنید. مدل ساعت‌دار اصلی تغییر نمی‌کند؛ شبیه‌سازی فیزیکی رقابت نیست."))
        prompt.setWordWrap(True)
        box.addWidget(prompt)
        self.inputs=QHBoxLayout()
        box.addLayout(self.inputs)
        row=QHBoxLayout()
        self.apply_button=QPushButton(self.t("Apply input event","اعمال رویداد ورودی"))
        self.apply_button.setObjectName("primary")
        self.apply_button.clicked.connect(self.apply)
        row.addWidget(self.apply_button)
        reset=QPushButton(self.t("Reset","بازنشانی"))
        reset.clicked.connect(self.reset)
        row.addWidget(reset)
        box.addLayout(row)
        self.outputs=QLabel()
        self.outputs.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        box.addWidget(self.outputs)
        self.status=QLabel()
        self.status.setWordWrap(True)
        box.addWidget(self.status)
        self.history=QTableWidget(0,4)
        self.history.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.history.setHorizontalHeaderLabels(["#",self.t("Inputs","ورودی‌ها"),"Q","Qbar"])
        self.history.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.history.verticalHeader().hide()
        self.history.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        box.addWidget(self.history,1)
        self.selector.currentIndexChanged.connect(self.reset)
        self.reset()

    def t(self,en,fa):
        return fa if self.fa else en

    def reset(self,*_):
        self.kind=self.selector.currentData()
        self.state=Storage()
        self.previous_clock=0
        self.events=0
        while self.inputs.count():
            item=self.inputs.takeAt(0)
            if item.widget():
                item.widget().hide()
                item.widget().deleteLater()
        self.buttons={}
        for pin in PINS[self.kind]:
            button=QCheckBox(pin)
            button.setChecked(pin.endswith("bar"))
            button.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
            self.buttons[pin]=button
            self.inputs.addWidget(button)
        self.note.setText(NOTES[self.kind][self.fa])
        self.history.setRowCount(0)
        self.refresh()

    def apply(self,*_):
        pins={pin:int(button.isChecked()) for pin,button in self.buttons.items()}
        self.state=step(self.kind,self.state,pins,self.previous_clock)
        self.previous_clock=pins.get("CLK",0)
        self.events+=1
        if self.history.rowCount()==32:
            self.history.removeRow(0)
        row=self.history.rowCount()
        self.history.insertRow(row)
        for col,value in enumerate((str(self.events)," ".join(f"{pin}={bit}" for pin,bit in pins.items()),
                                    self.symbol(self.state.q),self.symbol(self.state.qbar))):
            item=QTableWidgetItem(value)
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.history.setItem(row,col,item)
        self.history.scrollToBottom()
        self.refresh()

    @staticmethod
    def symbol(value):
        return "?" if value is None else str(value)

    def refresh(self):
        self.outputs.setText(f"Q = {self.symbol(self.state.q)}    |    Qbar = {self.symbol(self.state.qbar)}")
        if self.state.known:
            status=self.t("Known complementary outputs","خروجی‌های مکمل و مشخص")
        elif self.state.q is None:
            status=self.t("Unknown state — no physical outcome predicted","حالت نامعلوم؛ نتیجه فیزیکی پیش‌بینی نمی‌شود")
        else:
            status=self.t("Forbidden input — outputs are not complementary","ورودی ممنوع؛ خروجی‌ها مکمل نیستند")
        self.status.setText(status)
