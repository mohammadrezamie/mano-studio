"""A staged, pin-aware circuit editor embedded in Logic Lab."""
from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import (QWidget,QVBoxLayout,QHBoxLayout,QLabel,QLineEdit,
    QPushButton,QTableWidget,QTableWidgetItem,QComboBox,QSpinBox,QHeaderView)
from circuit_document import CircuitDocument, MAX_GATES, MAX_OUTPUTS
from logic_engine import ARITY, Gate


class CircuitEditor(QWidget):
    applied = Signal(object)
    cancelled = Signal()

    def __init__(self, fa=False):
        super().__init__()
        self.fa=fa
        layout=QVBoxLayout(self)
        label=QLabel(self.t("Edit connections by signal name. Each gate has its own input pins. Apply validates the entire circuit.",
            "اتصال‌ها را با نام سیگنال تعیین کنید. هر گیت پایه‌های ورودی خودش را دارد. اعمال، کل مدار را اعتبارسنجی می‌کند."))
        label.setWordWrap(True)
        layout.addWidget(label)
        row=QHBoxLayout()
        row.addWidget(QLabel(self.t("Input signals","سیگنال‌های ورودی")))
        self.inputs=QLineEdit()
        self.inputs.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.inputs.setPlaceholderText("A, B, Cin")
        row.addWidget(self.inputs,1)
        layout.addLayout(row)
        self.gates=QTableWidget(0,7)
        self.gates.setHorizontalHeaderLabels(["Signal","Gate","Pins","1","2","3","4"])
        self.gates.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.gates.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        layout.addWidget(self.gates,3)
        row=QHBoxLayout()
        for en,fa,fn in [("Add gate","افزودن گیت",self.add_gate),("Remove selected","حذف انتخاب",self.remove_gate),
                         ("Refresh pin choices","به‌روزرسانی اتصال‌ها",self.refresh_choices)]:
            button=QPushButton(self.t(en,fa))
            button.clicked.connect(fn)
            row.addWidget(button)
        row.addStretch()
        layout.addLayout(row)
        self.outputs=QTableWidget(0,2)
        self.outputs.setHorizontalHeaderLabels([self.t("Output name","نام خروجی"),self.t("Source signal","سیگنال مبدأ")])
        self.outputs.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.outputs.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        layout.addWidget(self.outputs,1)
        row=QHBoxLayout()
        for en,fa,fn in [("Add output","افزودن خروجی",self.add_output),("Remove output","حذف خروجی",self.remove_output),
                         ("Cancel","انصراف",self.cancelled.emit),("Apply circuit","اعمال مدار",self.apply)]:
            button=QPushButton(self.t(en,fa))
            button.clicked.connect(fn)
            if en=="Apply circuit":
                button.setObjectName("primary")
            row.addWidget(button)
        layout.addLayout(row)
        self.error=QLabel()
        self.error.setProperty("state","error")
        self.error.setWordWrap(True)
        layout.addWidget(self.error)

    def t(self,en,fa):
        return fa if self.fa else en

    def names(self):
        return [n.strip() for n in self.inputs.text().split(",") if n.strip()]

    def signal_choices(self):
        return list(dict.fromkeys(self.names()+[self.gates.item(r,0).text().strip()
                    for r in range(self.gates.rowCount()) if self.gates.item(r,0)]))

    def combo(self,value,choices):
        widget=QComboBox()
        widget.setEditable(True)
        widget.addItems([""]+[n for n in choices if n])
        widget.setCurrentText(value)
        return widget

    def add_gate(self, checked=False, gate=None):
        if self.gates.rowCount()>=MAX_GATES:
            return
        row=self.gates.rowCount()
        self.gates.insertRow(row)
        existing=set(self.signal_choices())
        name=next(f"g{i}" for i in range(1,MAX_GATES+2) if f"g{i}" not in existing)
        gate=gate or Gate(name,"AND",tuple((self.names()+["",""])[:2]))
        self.gates.setItem(row,0,QTableWidgetItem(gate.output))
        op=QComboBox()
        op.addItems(list(ARITY))
        op.setCurrentText(gate.op)
        self.gates.setCellWidget(row,1,op)
        count=QSpinBox()
        count.setRange(1,4)
        count.setValue(len(gate.inputs))
        self.gates.setCellWidget(row,2,count)
        for i in range(4):
            pin=self.combo(gate.inputs[i] if i<len(gate.inputs) else "",self.signal_choices())
            self.gates.setCellWidget(row,3+i,pin)
        def sync(*_):
            index=next((r for r in range(self.gates.rowCount()) if self.gates.cellWidget(r,1) is op),-1)
            if index<0:
                return
            unary=op.currentText()=="NOT"
            count.setRange(1,1) if unary else count.setRange(2,4)
            for i in range(4):
                self.gates.cellWidget(index,3+i).setEnabled(i<count.value())
        op.currentTextChanged.connect(sync)
        count.valueChanged.connect(sync)
        sync()

    def add_output(self,checked=False,output=None):
        if self.outputs.rowCount()>=MAX_OUTPUTS:
            return
        row=self.outputs.rowCount()
        self.outputs.insertRow(row)
        name,signal=output or (f"Y{row+1}","")
        self.outputs.setItem(row,0,QTableWidgetItem(name))
        self.outputs.setCellWidget(row,1,self.combo(signal,self.signal_choices()))

    def remove_gate(self):
        if self.gates.currentRow()>=0:
            self.gates.removeRow(self.gates.currentRow())
            self.refresh_choices()

    def remove_output(self):
        if self.outputs.currentRow()>=0:
            self.outputs.removeRow(self.outputs.currentRow())

    def refresh_choices(self):
        choices=self.signal_choices()
        for table,columns in [(self.gates,range(3,7)),(self.outputs,(1,))]:
            for row in range(table.rowCount()):
                for column in columns:
                    widget=table.cellWidget(row,column)
                    value=widget.currentText()
                    widget.blockSignals(True)
                    widget.clear()
                    widget.addItems([""]+choices)
                    widget.setCurrentText(value)
                    widget.blockSignals(False)

    def load(self,document):
        self.error.clear()
        self.inputs.setText(", ".join(document.inputs))
        self.gates.setRowCount(0)
        self.outputs.setRowCount(0)
        for gate in document.gates:
            self.add_gate(gate=gate)
        for output in document.outputs:
            self.add_output(output=output)
        self.refresh_choices()

    def document(self):
        gates=[]
        for r in range(self.gates.rowCount()):
            count=self.gates.cellWidget(r,2).value()
            gates.append(Gate(self.gates.item(r,0).text().strip(),
                              self.gates.cellWidget(r,1).currentText(),
                              tuple(self.gates.cellWidget(r,3+i).currentText().strip() for i in range(count))))
        outputs=tuple((self.outputs.item(r,0).text().strip(),self.outputs.cellWidget(r,1).currentText().strip())
                      for r in range(self.outputs.rowCount()))
        return CircuitDocument(tuple(self.names()),tuple(gates),outputs)

    def apply(self):
        try:
            document=self.document()
            document.compile()
        except ValueError as exc:
            self.error.setText(self.t("Cannot apply: ","امکان اعمال وجود ندارد: ")+str(exc))
            return
        self.error.clear()
        self.applied.emit(document)
