"""Read-only timing-group inspection of real CPU events."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget,QVBoxLayout,QHBoxLayout,QLabel,QTableWidget,QTableWidgetItem,QHeaderView,QAbstractItemView,QSplitter,QPushButton

class CycleView(QWidget):
    def __init__(self,fa=False,forward=None,backward=None):
        super().__init__()
        self.fa=fa
        self.current_trace=None
        layout=QVBoxLayout(self)
        self.note=QLabel(self.t("Execute one timing group at a time or inspect recorded state. SC, interrupt latch R and electrical delays are not modeled.","هر گروه زمانی را جداگانه اجرا کنید یا وضعیت ثبت‌شده را بررسی کنید. SC، ثبات وقفه R و تأخیر الکتریکی مدل نشده‌اند."))
        self.note.setWordWrap(True);layout.addWidget(self.note)
        controls=QHBoxLayout()
        self.back_button=QPushButton(self.t("Previous timing","زمان قبلی"))
        self.step_button=QPushButton(self.t("Next timing","زمان بعدی"))
        self.step_button.setObjectName("primary")
        if backward:self.back_button.clicked.connect(backward)
        if forward:self.step_button.clicked.connect(forward)
        controls.addWidget(self.back_button);controls.addWidget(self.step_button)
        controls.addStretch();layout.addLayout(controls)
        self.title=QLabel();layout.addWidget(self.title)
        split=QSplitter(Qt.Orientation.Horizontal)
        self.groups=QTableWidget(0,3)
        self.groups.setHorizontalHeaderLabels([self.t("Timing","زمان"),self.t("Phase","مرحله"),"RTL"])
        self.groups.horizontalHeader().setSectionResizeMode(2,QHeaderView.ResizeMode.Stretch)
        self.groups.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.detail=QTableWidget(0,3)
        self.detail.setHorizontalHeaderLabels([self.t("Register","ثبات"),self.t("Before","قبل"),self.t("After","بعد")])
        self.detail.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        for table in (self.groups,self.detail):
            table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
            table.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
            split.addWidget(table)
        split.setSizes([530,300]);layout.addWidget(split,1)
        self.memory=QLabel();self.memory.setWordWrap(True);layout.addWidget(self.memory)
        self.groups.currentCellChanged.connect(lambda row,*_:self.select(row))
        self.show_event(None)
    def t(self,en,fa):return fa if self.fa else en
    def show_event(self,event,partial=False):
        self.current_trace=event
        self.groups.setRowCount(0);self.detail.setRowCount(0);self.memory.clear()
        if event is None:
            self.title.setText(self.t("Execute an instruction or select a debugger row.","یک دستور اجرا کنید یا ردیفی از اشکال‌زدا انتخاب کنید."));return
        self.title.setText(f"{event.address:03X} · {event.mnemonic} · "+self.t("Timing groups: ","گروه‌های زمانی: ")+str(len(event.microevents)) + (" · "+self.t("In progress","در حال اجرا") if partial else ""))
        names={"fetch":self.t("Fetch","واکشی"),"decode":self.t("Decode","رمزگشایی"),"direct":self.t("Direct","مستقیم"),"indirect":self.t("Indirect","غیرمستقیم"),"execute":self.t("Execute","اجرا"),"register":self.t("Register","ثبات"),"io":self.t("I/O","ورودی/خروجی"),"interrupt":self.t("Interrupt","وقفه")}
        self.groups.setRowCount(len(event.microevents))
        for i,g in enumerate(event.microevents):
            rtl=self.t("No transfer","بدون انتقال") if g.phase=="direct" else g.rtl
            for j,v in enumerate((f"T{g.timing}",names[g.phase],rtl)):
                item=QTableWidgetItem(v);item.setToolTip(v);self.groups.setItem(i,j,item)
        if event.microevents:
            row=len(event.microevents)-1 if partial else 0
            self.groups.setCurrentCell(row,0);self.select(row)
    def select(self,row):
        self.detail.setRowCount(0);self.memory.clear()
        if self.current_trace is None or not 0<=row<len(self.current_trace.microevents):return
        g=self.current_trace.microevents[row]
        names=list(g.before)
        self.detail.setRowCount(len(names))
        for i,name in enumerate(names):
            width=3 if name in ("PC","AR") else 4 if name in ("IR","AC","DR","TR") else 2 if name in ("INPR","OUTR") else 1
            for j,value in enumerate((name,f"{g.before[name]:0{width}X}",f"{g.after[name]:0{width}X}")):
                item=QTableWidgetItem(value)
                if g.before[name]!=g.after[name]:
                    font=item.font();font.setBold(True);item.setFont(font)
                self.detail.setItem(i,j,item)
        reads=", ".join(f"M[{a:03X}] = {v:04X}" for a,v in g.reads) or "—"
        writes=", ".join(f"M[{a:03X}]: {old:04X} → {new:04X}" for a,old,new in g.writes) or "—"
        self.memory.setText(self.t("Read: ","خواندن: ")+reads+"\n"+self.t("Write: ","نوشتن: ")+writes)
