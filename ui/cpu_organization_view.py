"""Chapter 8 interactive register datapath and stack, independent teaching models."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QWidget,QVBoxLayout,QHBoxLayout,QLabel,QComboBox,QSpinBox,
    QTableWidget,QTableWidgetItem,QHeaderView,QAbstractItemView,QPushButton,QTabWidget,QPlainTextEdit)
from cpu_organization import RegisterFile,RegisterControl,RegisterStack,MemoryStack,OPR,ADDRESS_MODES,resolve_address
from ui.motion import MotionTabs
from microprogram import parse_image
from ui.expression_view import ExpressionView


def word_input():
    box=QSpinBox();box.setRange(0,65535);box.setDisplayIntegerBase(16)
    return box


class OrganizationView(QWidget):
    def __init__(self,fa=False):
        super().__init__()
        self.fa=fa
        layout=QVBoxLayout(self)
        self.tabs=tabs=MotionTabs();layout.addWidget(tabs)
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
        self.stack_note=note=QLabel(self.t("64-word ascending stack. PUSH increments SP then writes; POP reads then decrements. SP wraps at 64. FULL and EMPTY distinguish SP=0 states.",
            "پشته صعودی ۶۴ کلمه‌ای. PUSH ابتدا SP را افزایش داده و سپس می‌نویسد؛ POP ابتدا می‌خواند و سپس SP را کاهش می‌دهد. FULL و EMPTY دو حالت SP=0 را متمایز می‌کنند."))
        note.setWordWrap(True);body.addWidget(note)
        row=QHBoxLayout()
        self.stack_mode=QComboBox();self.stack_mode.addItem(self.t("Register stack","پشته ثباتی"),"register");self.stack_mode.addItem(self.t("Memory stack","پشته حافظه‌ای"),"memory");row.addWidget(self.stack_mode)
        self.stack_input=word_input();row.addWidget(QLabel("DR"));row.addWidget(self.stack_input)
        for en,fa_label,fn in [("PUSH","PUSH",self.push),("POP","POP",self.pop),("Reset","بازنشانی",self.reset_stack)]:
            b=QPushButton(self.t(en,fa_label));b.clicked.connect(fn);row.addWidget(b)
        body.addLayout(row)
        self.stack_state=QLabel();self.stack_state.setWordWrap(True);body.addWidget(self.stack_state)
        self.stack_status=QLabel();self.stack_status.setWordWrap(True);body.addWidget(self.stack_status)
        self.stack_table=self.table(64,[self.t("Address","آدرس"),self.t("Word HEX","کلمه هگز"),self.t("State","وضعیت")])
        body.addWidget(self.stack_table,1)
        tabs.addTab(page,self.t("Stacks","پشته‌ها"))
        self.stack_mode.currentIndexChanged.connect(self.reset_stack)
        self.refresh_stack()
        tabs.addTab(self.address_page(),self.t("Addressing modes","حالت‌های آدرس‌دهی"))
        self.expression_view=ExpressionView(self.fa)
        tabs.addTab(self.expression_view,self.t("Instruction formats","قالب دستورها"))

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
        memory=isinstance(s,MemoryStack)
        self.stack_state.setText(f"SP={s.sp:04X}" if memory else f"SP={s.sp:06b} ({s.sp})")
        self.stack_state.setText(self.stack_state.text()+f" | FULL={int(s.full)} | EMPTY={int(s.empty)} | {s.depth}/64")
        for row in range(64):
            address=s.high-row if memory else (row+1)&63
            state=self.t("Occupied","اشغال") if s.occupied(address) else self.t("Unused","خالی")
            if not s.empty and address==s.sp:state+=" · SP"
            word=s.words.get(address,0) if memory else s.words[address]
            for col,value in enumerate((f"{address:04X}" if memory else f"{address:02X}",f"{word:04X}",state)):
                self.stack_table.setItem(row,col,QTableWidgetItem(value))
        if not s.empty:self.stack_table.scrollToItem(self.stack_table.item(s.high-s.sp if memory else (s.sp-1)&63,0))

    def reset_stack(self,*_):
        memory=self.stack_mode.currentData()=="memory"
        self.stack=MemoryStack() if memory else RegisterStack()
        self.stack_note.setText(self.t("Descending memory stack 0400–043F (HEX). PUSH: SP−1 then write; POP: read then SP+1. Empty SP=0440. Bounds prevent collision.","پشته حافظه‌ای نزولی ۰۴۰۰ تا ۰۴۳F هگز. PUSH ابتدا کاهش SP سپس نوشتن؛ POP ابتدا خواندن سپس افزایش SP. حالت خالی SP=0440؛ محدوده محافظت می‌شود.") if memory else self.t("64-word ascending register stack; PUSH increments SP, POP decrements SP. FULL and EMPTY distinguish SP=0 states.","پشته ثباتی صعودی ۶۴ کلمه‌ای؛ PUSH افزایش و POP کاهش SP. FULL و EMPTY دو حالت SP=0 را متمایز می‌کنند."))
        self.refresh_stack();self.stack_status.clear()

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


    def address_page(self):
        page=QWidget();body=QVBoxLayout(page)
        note=QLabel(self.t("16-bit word addresses. PC is after instruction fetch; A is raw HEX, signed displacement for relative/indexed/base. Unspecified memory is zero. Evaluate commits auto-update of R only.",
            "آدرس کلمه ۱۶ بیتی. PC پس از واکشی دستور است؛ A هگز خام و در حالت نسبی/اندیسی/پایه جابجایی علامت‌دار است. حافظه تعریف‌نشده صفر است. محاسبه فقط تغییر خودکار R را اعمال می‌کند."))
        note.setWordWrap(True);body.addWidget(note)
        row=QHBoxLayout();self.address_mode=QComboBox()
        labels=("ضمنی","فوری","ثباتی","غیرمستقیم ثباتی","افزایش خودکار","کاهش خودکار","مستقیم","غیرمستقیم","نسبی","اندیسی","پایه")
        for mode,label in zip(ADDRESS_MODES,labels):self.address_mode.addItem(label if self.fa else mode.replace("_"," ").title(),mode)
        row.addWidget(self.address_mode)
        self.address_field=word_input();self.address_register=word_input();self.address_pc=word_input()
        for name,box in (("A",self.address_field),("R / IX / BR",self.address_register),("PC",self.address_pc)):
            row.addWidget(QLabel(name));row.addWidget(box)
        body.addLayout(row)
        row=QHBoxLayout()
        row.addWidget(QLabel(self.t("Memory HEX address:word","حافظه هگز آدرس:کلمه")))
        evaluate=QPushButton(self.t("Evaluate","محاسبه"));evaluate.clicked.connect(self.evaluate_address);row.addWidget(evaluate)
        body.addLayout(row)
        self.address_memory=QPlainTextEdit("0100:0200\n0200:ABCD")
        self.address_memory.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.address_memory.setMaximumHeight(80);body.addWidget(self.address_memory)
        self.address_result=QLabel();self.address_result.setWordWrap(True);body.addWidget(self.address_result)
        self.address_reads=self.table(0,[self.t("Read address","آدرس خواندن"),self.t("Word","کلمه")])
        body.addWidget(self.address_reads,1)
        self.last_address=None
        for box in (self.address_field,self.address_register,self.address_pc):box.valueChanged.connect(self.clear_address)
        self.address_mode.currentIndexChanged.connect(self.clear_address)
        self.address_memory.textChanged.connect(self.clear_address)
        return page

    def clear_address(self,*_):
        self.last_address=None;self.address_result.clear();self.address_reads.setRowCount(0)

    def evaluate_address(self):
        self.clear_address()
        try:
            memory=parse_image(self.address_memory.toPlainText(),65536,65536)
            result=resolve_address(self.address_mode.currentData(),self.address_field.value(),self.address_register.value(),self.address_pc.value(),memory)
        except ValueError:
            self.address_result.setText(self.t("Invalid memory image or operand.","تصویر حافظه یا عملوند نامعتبر است."));return
        self.address_register.blockSignals(True)
        self.address_register.setValue(result.register_after)
        self.address_register.blockSignals(False)
        self.last_address=result
        def hexword(v):return "—" if v is None else f"{v:04X}"
        self.address_result.setText(f"{result.expression} | EA={hexword(result.effective_address)} | "+self.t("Operand","عملوند")+f"={hexword(result.operand)} | R: {result.register_before:04X} → {result.register_after:04X}")
        self.address_reads.setRowCount(len(result.reads))
        for row,(a,v) in enumerate(result.reads):
            for col,value in enumerate((f"{a:04X}",f"{v:04X}")):
                self.address_reads.setItem(row,col,QTableWidgetItem(value))
