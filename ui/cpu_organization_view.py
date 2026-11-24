"""Chapter 8 interactive register datapath and stack, independent teaching models."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QWidget,QVBoxLayout,QHBoxLayout,QLabel,QComboBox,QSpinBox,
    QTableWidget,QTableWidgetItem,QHeaderView,QAbstractItemView,QPushButton,QTabWidget)
from cpu_organization import RegisterFile,RegisterControl,RegisterStack,OPR


def word_input():
    box=QSpinBox();box.setRange(0,65535);box.setDisplayIntegerBase(16)
    return box


class OrganizationView(QWidget):
    def __init__(self,fa=False):
        super().__init__()
        self.fa=fa
        layout=QVBoxLayout(self)
        tabs=QTabWidget();layout.addWidget(tabs)
        self.registers=RegisterFile()
        self.stack=RegisterStack()
        page=QWidget();body=QVBoxLayout(page)
        note=QLabel(self.t("Two 8:1 source selectors, ALU, and destination decoder. Source 000 = external input; destination 000 = no write. Separate Chapter 8 model.",
            "دو انتخاب‌گر منبع ۸ به ۱، ALU و دیکدر مقصد. منبع ۰۰۰ ورودی خارجی و مقصد ۰۰۰ بدون نوشتن است. مدل مستقل فصل هشتم."))
        note.setWordWrap(True);body.addWidget(note)
        row=QHBoxLayout()
        self.selectors=[]
        for name in ("SELA","SELB","SELD"):
            box=QComboBox()
            box.addItem(self.t("Input","ورودی") if name!="SELD" else self.t("No write","بدون نوشتن"),0)
            for i in range(1,8):box.addItem(f"R{i}",i)
            row.addWidget(QLabel(name));row.addWidget(box);self.selectors.append(box)
        self.op=QComboBox()
        for code,name in OPR.items():self.op.addItem(name,code)
        row.addWidget(QLabel("OPR"));row.addWidget(self.op)
        body.addLayout(row)
        row=QHBoxLayout()
        self.external=word_input();row.addWidget(QLabel(self.t("Input HEX","ورودی هگز")));row.addWidget(self.external)
        run=QPushButton(self.t("Execute edge","اجرای لبه ساعت"));run.clicked.connect(self.execute);row.addWidget(run)
        reset=QPushButton(self.t("Reset","بازنشانی"));reset.clicked.connect(self.reset_regs);row.addWidget(reset)
        body.addLayout(row)
        self.control=QLabel();self.control.setWordWrap(True);body.addWidget(self.control)
        self.result=QLabel();self.result.setWordWrap(True);body.addWidget(self.result)
        self.reg_table=self.table(7,[self.t("Register","ثبات"),self.t("Before","قبل"),self.t("After","بعد")])
        body.addWidget(self.reg_table,1)
        tabs.addTab(page,self.t("General registers","ثبات‌های عمومی"))
        for box in self.selectors+[self.op]:box.currentIndexChanged.connect(self.preview)
        self.preview();self.reset_regs()
        page=QWidget();body=QVBoxLayout(page)
        note=QLabel(self.t("64-word ascending stack. PUSH increments SP then writes; POP reads then decrements. SP wraps at 64. FULL and EMPTY distinguish SP=0 states.",
            "پشته صعودی ۶۴ کلمه‌ای. PUSH ابتدا SP را افزایش داده و سپس می‌نویسد؛ POP ابتدا می‌خواند و سپس SP را کاهش می‌دهد. FULL و EMPTY دو حالت SP=0 را متمایز می‌کنند."))
        note.setWordWrap(True);body.addWidget(note)
        row=QHBoxLayout()
        self.stack_input=word_input();row.addWidget(QLabel("DR"));row.addWidget(self.stack_input)
        for en,fa_label,fn in [("PUSH","PUSH",self.push),("POP","POP",self.pop),("Reset","بازنشانی",self.reset_stack)]:
            b=QPushButton(self.t(en,fa_label));b.clicked.connect(fn);row.addWidget(b)
        body.addLayout(row)
        self.stack_state=QLabel();self.stack_state.setWordWrap(True);body.addWidget(self.stack_state)
        self.stack_status=QLabel();self.stack_status.setWordWrap(True);body.addWidget(self.stack_status)
        self.stack_table=self.table(64,[self.t("Address","آدرس"),self.t("Word HEX","کلمه هگز"),self.t("State","وضعیت")])
        body.addWidget(self.stack_table,1)
        tabs.addTab(page,self.t("Register stack","پشته ثباتی"))
        self.refresh_stack()

    def t(self,en,fa):return fa if self.fa else en

    def table(self,rows,headers):
        table=QTableWidget(rows,len(headers));table.setHorizontalHeaderLabels(headers)
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        return table

    def current_control(self):
        return RegisterControl(*(box.currentData() for box in self.selectors),self.op.currentData())

    def preview(self,*_):
        c=self.current_control()
        self.control.setText(f"{c.sela:03b} | {c.selb:03b} | {c.seld:03b} | {c.opr:05b}   =   {c.encode():04X}")

    def show_regs(self,before,after):
        for row,(a,b) in enumerate(zip(before,after)):
            for col,value in enumerate((f"R{row+1}",f"{a:04X}",f"{b:04X}")):
                self.reg_table.setItem(row,col,QTableWidgetItem(value))

    def reset_regs(self):
        self.registers=RegisterFile()
        self.show_regs(self.registers.words,self.registers.words);self.result.clear()

    def execute(self):
        event=self.registers.transfer(self.current_control(),self.external.value())
        self.show_regs(event.before,event.after)
        self.result.setText(f"A={event.a:04X} | B={event.b:04X} | {event.operation} | OUT={event.output:04X}")

    def refresh_stack(self):
        s=self.stack
        self.stack_state.setText(f"SP={s.sp:06b} ({s.sp}) | FULL={int(s.full)} | EMPTY={int(s.empty)} | {s.depth}/64")
        for row in range(64):
            address=(row+1)&63
            state=self.t("Occupied","اشغال") if s.occupied(address) else self.t("Unused","خالی")
            if not s.empty and address==s.sp:state+=" · SP"
            for col,value in enumerate((f"{address:02X}",f"{s.words[address]:04X}",state)):
                self.stack_table.setItem(row,col,QTableWidgetItem(value))
        if not s.empty:self.stack_table.scrollToItem(self.stack_table.item((s.sp-1)&63,0))

    def reset_stack(self):
        self.stack=RegisterStack();self.refresh_stack();self.stack_status.clear()

    def push(self):
        if self.stack.full:
            self.stack_status.setText(self.t("Stack overflow; no change.","سرریز پشته؛ بدون تغییر."));return
        e=self.stack.push(self.stack_input.value())
        self.refresh_stack();self.stack_status.setText(f"M[{e.address:02X}] ← {e.value:04X}")

    def pop(self):
        if self.stack.empty:
            self.stack_status.setText(self.t("Stack underflow; no change.","کمبود پشته؛ بدون تغییر."));return
        e=self.stack.pop();self.stack_input.setValue(e.value)
        self.refresh_stack();self.stack_status.setText(f"DR ← M[{e.address:02X}] = {e.value:04X}")
