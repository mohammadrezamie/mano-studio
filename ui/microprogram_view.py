"""Interactive Chapter 7 control memory, independent of the Basic Computer."""
from PySide6.QtCore import Qt
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import (QWidget,QVBoxLayout,QHBoxLayout,QLabel,QPlainTextEdit,
    QTableWidget,QTableWidgetItem,QHeaderView,QAbstractItemView,QPushButton,QSpinBox,QComboBox,QTabWidget)
from microprogram import MicroComputer,parse_image,demo_images,CONDITIONS,BRANCHES
from microassembler import assemble_micro, DEMO_SOURCE, full_demo
from microprogram_history import MicroHistory
from ui.microsequencer_view import MicrosequencerView
from ui.microinstruction_builder import MicroinstructionBuilder


class MicroprogramView(QWidget):
    def __init__(self,fa=False):
        super().__init__()
        self.fa=fa
        self.model=None
        self.history=None
        self.last=None
        self.source_lines={}
        layout=QVBoxLayout(self)
        note=QLabel(self.t("Chapter 7 model: 128 × 20 control store; 11-bit PC/AR. Not the Basic Computer ISA. Edit raw or symbolic control source, load, then execute one microinstruction.",
            "مدل فصل هفتم: حافظه کنترل ۱۲۸ × ۲۰ و PC/AR یازده‌بیتی. این مدل با پردازنده پایه متفاوت است. متن خام یا نمادین حافظه کنترل را ویرایش و بارگذاری کنید و ریزدستور را اجرا کنید."))
        note.setWordWrap(True);layout.addWidget(note)
        mode_row=QHBoxLayout()
        self.mode=QComboBox()
        self.mode.addItem(self.t("Raw HEX","هگز خام"),"raw")
        self.mode.addItem(self.t("Symbolic microassembly","اسمبلی نمادین ریزبرنامه"),"symbolic")
        mode_row.addWidget(self.mode)
        self.syntax=QLabel();self.syntax.setWordWrap(True);mode_row.addWidget(self.syntax,1)
        layout.addLayout(mode_row)
        row=QHBoxLayout()
        self.control=QPlainTextEdit()
        self.data=QPlainTextEdit()
        for edit,en,fa_label in [(self.control,"Control source","متن حافظه کنترل"),(self.data,"Data memory (HEX)","حافظه داده (هگز)")]:
            col=QVBoxLayout();col.addWidget(QLabel(self.t(en,fa_label)))
            edit.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
            edit.setAccessibleName(self.t(en,fa_label))
            edit.setMaximumHeight(110);col.addWidget(edit);row.addLayout(col)
        layout.addLayout(row)
        row=QHBoxLayout()
        row.addWidget(QLabel("CAR"))
        self.entry=QSpinBox();self.entry.setRange(0,127);self.entry.setValue(64);row.addWidget(self.entry)
        for en,fa_label,fn in [("Example","مثال",self.example),("Load / Reset","بارگذاری / بازنشانی",self.load),("Previous microinstruction","ریزدستور قبلی",self.back),("Next microinstruction","ریزدستور بعدی",self.step)]:
            button=QPushButton(self.t(en,fa_label));button.clicked.connect(fn);row.addWidget(button)
            if fn==self.step:self.step_button=button
            if fn==self.back:self.back_button=button
        layout.addLayout(row)
        self.fields=QLabel();self.fields.setWordWrap(True);self.fields.setLayoutDirection(Qt.LayoutDirection.LeftToRight);layout.addWidget(self.fields)
        self.table=QTableWidget(0,3)
        self.table.setHorizontalHeaderLabels([self.t("Register","ثبات"),self.t("Before (HEX)","قبل (هگز)"),self.t("After (HEX)","بعد (هگز)")])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.detail_tabs=QTabWidget()
        self.detail_tabs.addTab(self.table,self.t("Registers","ثبات‌ها"))
        self.sequencer=MicrosequencerView(fa)
        self.detail_tabs.addTab(self.sequencer,self.t("Address selector","انتخاب آدرس"))
        self.trace=QTableWidget(0,5)
        self.trace.setHorizontalHeaderLabels(["#","CAR","HEX","Source",self.t("Next CAR","CAR بعدی")])
        if fa:self.trace.setHorizontalHeaderItem(3,QTableWidgetItem("منبع"))
        self.trace.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.trace.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.trace.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.detail_tabs.addTab(self.trace,self.t("History","تاریخچه"))
        self.builder=MicroinstructionBuilder(fa,self.append_word)
        self.detail_tabs.addTab(self.builder,self.t("Build control word","ساخت کلمه کنترل"))
        self.trace.cellClicked.connect(self.inspect_history)
        layout.addWidget(self.detail_tabs,1)
        self.listing=QPlainTextEdit();self.listing.setReadOnly(True);self.listing.setMaximumHeight(65)
        self.listing.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.listing.setAccessibleName(self.t("Assembled control image","تصویر اسمبل‌شده کنترل"));layout.addWidget(self.listing)
        self.status=QLabel();self.status.setWordWrap(True);layout.addWidget(self.status)
        self.control.textChanged.connect(self.invalidate);self.data.textChanged.connect(self.invalidate)
        self.entry.valueChanged.connect(self.invalidate)
        self.mode.currentIndexChanged.connect(self.mode_changed)
        self.mode_changed()
        self.example()

    def t(self,en,fa):return fa if self.fa else en

    def invalidate(self,*_):
        self.model=self.last=self.history=None
        self.source_lines={}
        self.sequencer.set_trace(None);self.trace.setRowCount(0);self.back_button.setEnabled(False)
        self.table.setRowCount(0);self.fields.clear();self.listing.clear();self.step_button.setEnabled(False)
        self.status.setText(self.t("Images changed. Load again.","تصویر حافظه تغییر کرد؛ دوباره بارگذاری کنید."))

    def mode_changed(self,*_):
        symbolic=self.mode.currentData()=="symbolic"
        self.syntax.setText(self.t("ORG decimal; label: operations CD BR AD; NEXT","ORG ده‌دهی؛ برچسب: عملیات CD BR AD؛ NEXT") if symbolic else self.t("HEX address:word","آدرس:کلمه هگز"))
        # Changing notation never silently replaces user source.
        self.invalidate()

    def example(self):
        if self.mode.currentData()=="symbolic":
            c,d=full_demo()
            self.control.setPlainText(DEMO_SOURCE)
        else:
            c,d=demo_images()
            self.control.setPlainText("\n".join(f"{a:02X}:{w:05X}" for a,w in sorted(c.items())))
        self.data.setPlainText("\n".join(f"{a:03X}:{w:04X}" for a,w in sorted(d.items())))
        self.entry.setValue(64);self.load()

    def load(self):
        self.invalidate()
        try:
            if self.mode.currentData()=="symbolic":
                result=assemble_micro(self.control.toPlainText())
                if not result.ok:
                    names={"LABEL":"برچسب نامعتبر یا تکراری","ADDRESS":"آدرس نامعتبر","OVERLAP":"آدرس تکراری یا خارج از محدوده","SYNTAX":"ساختار ریزدستور نامعتبر","OPERATION":"ریزعملیات نامعتبر","CONFLICT":"عملیات متعارض","TARGET":"مقصد نامعتبر","EMPTY":"ریزبرنامه خالی"}
                    self.status.setText("\n".join(f"{e.line}: {names[e.code] if self.fa else e.code} {e.detail}" for e in result.errors[:8]))
                    return
                c=result.words
                source_lines=result.source_lines
            else:
                c=parse_image(self.control.toPlainText(),128,1<<20)
                source_lines={int(line.split(':',1)[0].strip(),16):i for i,raw in enumerate(self.control.toPlainText().splitlines(),1) if (line:=raw.split('#',1)[0].strip())}
            self.model=MicroComputer(c,parse_image(self.data.toPlainText(),2048,65536),self.entry.value())
            self.listing.setPlainText("\n".join(f"{a:02X}:{w:05X}" for a,w in sorted(c.items())))
        except ValueError as e:
            self.status.setText(self.t(str(e),"تصویر حافظه نامعتبر است؛ آدرس‌ها و کلمات هگز را بررسی کنید."));return
        self.source_lines=source_lines
        self.history=MicroHistory(self.model)
        self.step_button.setEnabled(True)
        regs=self.model.registers();self.show_regs(regs,regs)
        self.status.setText(self.t("Ready.","آماده."))

    def show_regs(self,before,after):
        self.table.setRowCount(len(before))
        for i,k in enumerate(before):
            for j,v in enumerate((k,f"{before[k]:04X}",f"{after[k]:04X}")):
                item=QTableWidgetItem(v)
                if before[k]!=after[k]:
                    font=item.font();font.setBold(True);item.setFont(font)
                self.table.setItem(i,j,item)

    def step(self):
        if self.model is None:return
        try:g=self.history.step()
        except ValueError as e:
            self.status.setText(self.t(str(e),"ریزدستور نامعتبر، مقداردهی‌نشده یا دارای عملیات متعارض است."));return
        self.show_step(g)
        self.refresh_history()

    def show_step(self,g):
        self.last=g;self.sequencer.set_trace(g);self.show_regs(g.before,g.after)
        self.select_source(g.before['CAR'])
        m=g.instruction
        self.fields.setText(f"F1 {m.f1:03b} | F2 {m.f2:03b} | F3 {m.f3:03b} | CD {m.cd:02b} | BR {m.br:02b} | AD {m.ad:07b}\n"
            +(", ".join(m.operations) or "NOP")+f" | {CONDITIONS[m.cd]}={int(g.condition)} | {BRANCHES[m.br]} | CAR ← {g.next_source} ({g.after['CAR']:02X})")
        accesses=[f"M[{a:03X}] → {v:04X}" for a,v in g.reads]+[f"M[{a:03X}]: {old:04X} → {v:04X}" for a,old,v in g.writes]
        self.status.setText(" · ".join(accesses) or self.t("No memory access.","بدون دسترسی حافظه."))


    def refresh_history(self):
        entries=self.history.entries
        self.trace.setRowCount(len(entries))
        for row,(number,event) in enumerate(entries):
            values=(number,f"{event.before['CAR']:02X}",f"{event.word:05X}",event.next_source,f"{event.after['CAR']:02X}")
            for col,value in enumerate(values):
                self.trace.setItem(row,col,QTableWidgetItem(str(value)))
        if entries:self.trace.scrollToBottom()
        self.back_button.setEnabled(bool(entries))

    def back(self):
        if self.history is None or self.history.back() is None:return
        if self.history.entries:
            self.show_step(self.history.entries[-1][1])
        else:
            self.last=None
            self.fields.clear()
            self.sequencer.set_trace(None)
            regs=self.model.registers()
            self.show_regs(regs,regs)
        self.refresh_history()
        self.status.setText(self.t("Microinstruction reversed.","ریزدستور واگرد شد."))


    def append_word(self,address,word,symbolic):
        original=self.control.toPlainText()
        addition=symbolic if self.mode.currentData()=="symbolic" else f"{address:02X}:{word:05X}"
        combined=original.rstrip()+("\n" if original.strip() else "")+addition
        if self.mode.currentData()=="symbolic":
            if not assemble_micro(combined).ok:return False
        else:
            try:parse_image(combined,128,1<<20)
            except ValueError:return False
        self.control.setPlainText(combined)
        return True

    def select_source(self,address):
        line=self.source_lines.get(address)
        if line is not None:
            block=self.control.document().findBlockByNumber(line-1)
            if block.isValid():
                cursor=QTextCursor(block)
                cursor.select(QTextCursor.SelectionType.LineUnderCursor)
                self.control.setTextCursor(cursor)
                self.control.ensureCursorVisible()

    def inspect_history(self,row,*_):
        if self.history is None or not 0<=row<len(self.history.entries):return
        number,event=self.history.entries[row]
        self.show_step(event)
        self.status.setText(self.t("Historical step: ","مرحله تاریخی: ")+str(number)+" | "+self.t("Live CAR: ","CAR فعلی: ")+f"{self.model.car:02X}")
