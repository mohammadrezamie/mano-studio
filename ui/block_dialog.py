"""One focused dialog for inserting an existing combinational preset."""
from PySide6.QtWidgets import (QDialog,QVBoxLayout,QFormLayout,QLabel,QComboBox,
    QLineEdit,QDialogButtonBox,QWidget,QScrollArea,QPushButton,QFileDialog,QMessageBox)
from PySide6.QtCore import Qt
from logic_engine import CIRCUITS
from circuit_document import CircuitDocument
from circuit_composition import compose
from native_circuit import load_circuit
from classic_samples import SAMPLES, load_sample
from pathlib import Path


class BlockDialog(QDialog):
    def __init__(self,base,fa=False,parent=None):
        super().__init__(parent)
        self.base,self.fa=base,fa
        self.result_document=None
        self.setWindowTitle(self.t("Insert circuit block","درج بلوک مدار"))
        layout=QVBoxLayout(self)
        note=QLabel(self.t("Choose a preset, saved sample or circuit file. Connect each input to an existing signal or expose a new input. Original outputs remain; new gate and output names use the prefix. Layout is regenerated.",
            "مدار آماده، نمونه یا فایل مدار را انتخاب کنید. هر ورودی را به سیگنال موجود وصل کنید یا ورودی جدید بسازید. خروجی‌های قبلی حفظ و نام‌های جدید پیشونددار می‌شوند. چیدمان دوباره ساخته می‌شود."))
        note.setWordWrap(True);layout.addWidget(note)
        form=QFormLayout()
        self.selector=QComboBox()
        for key,c in CIRCUITS.items():
            self.selector.addItem(c.title[fa],key)
        for sample in SAMPLES:
            self.selector.addItem(sample["title"][fa], "sample:"+sample["id"])
        self.imported=None
        form.addRow(self.t("Block","بلوک"),self.selector)
        browse=QPushButton(self.t("Load saved circuit…","بارگذاری مدار ذخیره‌شده…"))
        browse.clicked.connect(self.browse)
        form.addRow(browse)
        self.prefix=QLineEdit("b1")
        self.prefix.setMaxLength(12)
        self.prefix.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        form.addRow(self.t("Name prefix","پیشوند نام"),self.prefix)
        layout.addLayout(form)
        scroll=QScrollArea()
        scroll.setWidgetResizable(True)
        page=QWidget()
        self.ports=QFormLayout(page)
        scroll.setWidget(page)
        layout.addWidget(scroll,1)
        self.error=QLabel()
        self.error.setWordWrap(True)
        self.error.setProperty("state","error")
        layout.addWidget(self.error)
        buttons=QDialogButtonBox(QDialogButtonBox.StandardButton.Ok|QDialogButtonBox.StandardButton.Cancel)
        buttons.button(QDialogButtonBox.StandardButton.Ok).setText(self.t("Insert","درج"))
        buttons.button(QDialogButtonBox.StandardButton.Cancel).setText(self.t("Cancel","لغو"))
        buttons.accepted.connect(self.validate)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        self.selector.currentIndexChanged.connect(self.rebuild)
        self.resize(540,430)
        self.rebuild()

    def t(self,en,fa):
        return fa if self.fa else en

    def rebuild(self,*_):
        while self.ports.rowCount():
            self.ports.removeRow(0)
        self.error.clear()
        self.fields={}
        c=self.selected_block()
        signals=(*self.base.inputs,*(g.output for g in self.base.gates))
        for pin in c.inputs:
            field=QComboBox()
            field.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
            field.addItem(self.t("New input","ورودی جدید"),None)
            for signal in signals:
                field.addItem(signal,signal)
            self.fields[pin]=field
            self.ports.addRow(pin,field)

    def selected_block(self):
        key=self.selector.currentData()
        if key=="imported":
            return self.imported
        if key.startswith("sample:"):
            return load_sample(key.split(":",1)[1])
        return CircuitDocument.from_circuit(CIRCUITS[key])

    def browse(self):
        name,_=QFileDialog.getOpenFileName(self,self.t("Load block","بارگذاری بلوک"),"",
            "Mano Studio (*.mano);;Legacy circuit (*.mano-logic.json);;JSON (*.json)")
        if not name:
            return
        try:
            document=load_circuit(name)
        except (OSError,UnicodeError,ValueError):
            QMessageBox.warning(self,self.t("Invalid circuit","مدار نامعتبر"),
                self.t("The file could not be read or is not a supported circuit.","فایل خوانده نشد یا مدار پشتیبانی‌شده نیست."))
            return
        self.imported=document
        index=self.selector.findData("imported")
        if index<0:
            self.selector.addItem(Path(name).name,"imported")
            index=self.selector.findData("imported")
        else:
            self.selector.setItemText(index,Path(name).name)
        self.selector.setCurrentIndex(index)
        self.rebuild()

    def validate(self):
        try:
            block=self.selected_block()
            self.result_document=compose(self.base,block,self.prefix.text(),
                {pin:field.currentData() for pin,field in self.fields.items()})
        except ValueError:
            self.error.setText(self.t("Cannot insert: check the unique ASCII prefix, input mappings and editor limits (10 inputs, 96 gates, 16 outputs).",
                "درج ممکن نیست: پیشوند یکتای انگلیسی، اتصال ورودی‌ها و حدود ویرایشگر (۱۰ ورودی، ۹۶ گیت، ۱۶ خروجی) را بررسی کنید."))
            return
        self.accept()
