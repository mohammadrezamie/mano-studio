"""Chapter 11 DMA and FIFO controls using actual model events."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QWidget,QVBoxLayout,QHBoxLayout,QLabel,QComboBox,QSpinBox,QPushButton,
    QLineEdit,QTableWidget,QTableWidgetItem,QHeaderView,QAbstractItemView)
from dma_model import DMA,CircularFIFO
from memory_organization import MemoryArray


def table(headers):
    t=QTableWidget(0,len(headers))
    t.setHorizontalHeaderLabels(headers)
    t.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
    t.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
    t.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
    return t


class DMAView(QWidget):
    def __init__(self,fa=False,irq=None):
        super().__init__()
        self.fa=fa;self.irq=irq;self.model=None
        layout=QVBoxLayout(self)
        note=QLabel(self.t("16-bit words, 64-word RAM. DMA requests the bus, receives grant, transfers and releases. Cycle stealing inserts a CPU bus cycle. IRQ2 signals completion. The CPU is an abstract bus user.",
            "کلمات ۱۶ بیتی، RAM با ۶۴ کلمه. DMA گذرگاه را درخواست می‌کند، مجوز می‌گیرد، انتقال می‌دهد و آزاد می‌کند. در حالت سرقت چرخه، یک چرخه CPU بین انتقال‌ها قرار می‌گیرد. IRQ2 پایان انتقال را اعلام می‌کند. CPU مدل انتزاعی است."))
        note.setWordWrap(True);layout.addWidget(note)
        row=QHBoxLayout()
        self.direction=QComboBox()
        self.direction.addItem(self.t("Device → RAM","دستگاه به RAM"),"to_memory")
        self.direction.addItem(self.t("RAM → Device","RAM به دستگاه"),"from_memory")
        self.mode=QComboBox()
        self.mode.addItem(self.t("Burst","بلوک پیوسته"),"burst")
        self.mode.addItem(self.t("Cycle stealing","سرقت چرخه"),"cycle_steal")
        self.start=QSpinBox();self.start.setRange(0,63);self.start.setDisplayIntegerBase(16)
        row.addWidget(self.direction);row.addWidget(self.mode);row.addWidget(QLabel("AR HEX"));row.addWidget(self.start)
        layout.addLayout(row)
        row=QHBoxLayout()
        row.addWidget(QLabel(self.t("Source words HEX","کلمات مبدأ هگز")))
        self.words=QLineEdit("1234 ABCD 0000 00FF");self.words.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.words.setMaxLength(320);row.addWidget(self.words,1)
        for en,fa_label,fn in (("Load / Reset","بارگذاری / بازنشانی",self.load),("Next cycle","چرخه بعد",self.step),("Run","اجرا",self.run)):
            b=QPushButton(self.t(en,fa_label));b.clicked.connect(fn);row.addWidget(b)
        layout.addLayout(row)
        self.state=QLabel();self.state.setWordWrap(True);layout.addWidget(self.state)
        self.trace=table(["#",self.t("Action","عمل"),self.t("Bus owner","مالک گذرگاه"),"BR","BG","AR","DATA","WC","IRQ"])
        layout.addWidget(self.trace,1)
        self.result=QLabel();self.result.setWordWrap(True);layout.addWidget(self.result)
        self.status=QLabel();self.status.setWordWrap(True);layout.addWidget(self.status)
        for w in (self.direction,self.mode):w.currentIndexChanged.connect(self.invalidate)
        self.start.valueChanged.connect(self.invalidate);self.words.textChanged.connect(self.invalidate)
        self.load()

    def t(self,en,fa):return fa if self.fa else en

    def invalidate(self,*_):
        self.model=None;self.trace.setRowCount(0);self.state.clear();self.result.clear()
        self.status.setText(self.t("Inputs changed. Load again.","ورودی تغییر کرد؛ دوباره بارگذاری کنید."))

    def load(self):
        self.invalidate()
        try:
            import re
            tokens=self.words.text().split()
            if not tokens or any(not re.fullmatch(r"[0-9A-Fa-f]{1,4}",v) for v in tokens):raise ValueError("Invalid words")
            words=tuple(int(v,16) for v in tokens)
            memory=MemoryArray(4,8,4,2)
            start=self.start.value()
            direction=self.direction.currentData()
            device=words if direction=="to_memory" else ()
            model=DMA(memory,device,direction,start,len(words),self.mode.currentData())
            if direction=="from_memory":
                for i,v in enumerate(words):memory.write(start+i,v)
            self.model=model
        except ValueError:
            self.status.setText(self.t("Invalid words or range.","کلمات یا محدوده نامعتبر است."));return
        self.refresh();self.status.setText(self.t("Ready.","آماده."))

    def refresh(self):
        m=self.model
        self.state.setText(f"AR={m.address:02X} | WC={m.remaining} | "+self.t("Cycles","چرخه")+f": {m.cycles} | IRQ={int(m.irq)}")
        if m.direction=="to_memory":
            end=self.start.value()+len(self.words.text().split())
            values=[m.memory.read(i) for i in range(self.start.value(),end)]
        else:values=m.device
        self.result.setText(self.t("Destination words","کلمات مقصد")+": "+" ".join(f"{v:04X}" for v in values))

    def step(self):
        if self.model is None:return
        e=self.model.step()
        if e is None:return
        if e.irq and self.irq is not None:self.irq()
        labels={"request":"درخواست","grant":"مجوز","transfer":"انتقال","release":"آزادسازی","cpu_cycle":"چرخه CPU"}
        values=(e.number,labels[e.action] if self.fa else e.action,e.owner,int(e.request),int(e.grant),
                "—" if e.address is None else f"{e.address:02X}","—" if e.value is None else f"{e.value:04X}",e.remaining,int(e.irq))
        row=self.trace.rowCount();self.trace.insertRow(row)
        for col,value in enumerate(values):self.trace.setItem(row,col,QTableWidgetItem(str(value)))
        self.trace.scrollToBottom();self.refresh()
        self.status.setText(self.t("Complete.","تکمیل شد.") if self.model.done else "")

    def run(self):
        if self.model is not None:
            while not self.model.done:self.step()


class FIFOView(QWidget):
    def __init__(self,fa=False):
        super().__init__()
        self.fa=fa
        layout=QVBoxLayout(self)
        note=QLabel(self.t("Circular 16-bit FIFO. Read+write is allowed when full; no empty bypass. Invalid edges leave state unchanged.",
            "FIFO حلقوی ۱۶ بیتی. خواندن و نوشتن هم‌زمان در حالت پر مجاز است؛ عبور مستقیم در حالت خالی وجود ندارد. لبه نامعتبر وضعیت را تغییر نمی‌دهد."))
        note.setWordWrap(True);layout.addWidget(note)
        row=QHBoxLayout()
        self.capacity=QComboBox()
        for n in (4,8,16):self.capacity.addItem(str(n),n)
        self.capacity.setCurrentIndex(1);row.addWidget(self.capacity)
        self.value=QSpinBox();self.value.setRange(0,65535);self.value.setDisplayIntegerBase(16);row.addWidget(self.value)
        for en,fa_label,read,write in (("Write","نوشتن",False,True),("Read","خواندن",True,False),("Read + write","خواندن و نوشتن",True,True)):
            b=QPushButton(self.t(en,fa_label));b.clicked.connect(lambda checked=False,r=read,w=write:self.edge(r,w));row.addWidget(b)
        b=QPushButton(self.t("Reset","بازنشانی"));b.clicked.connect(self.reset);row.addWidget(b)
        layout.addLayout(row)
        self.state=QLabel();self.state.setWordWrap(True);layout.addWidget(self.state)
        self.cells=table([self.t("Cell","خانه"),"HEX",self.t("State","وضعیت")]);layout.addWidget(self.cells,1)
        self.result=QLabel();self.result.setWordWrap(True);layout.addWidget(self.result)
        self.status=QLabel();self.status.setWordWrap(True);layout.addWidget(self.status)
        self.capacity.currentIndexChanged.connect(self.reset)
        self.reset()

    def t(self,en,fa):return fa if self.fa else en

    def reset(self,*_):
        self.model=CircularFIFO(self.capacity.currentData())
        self.status.clear();self.refresh()

    def refresh(self):
        m=self.model
        self.state.setText(f"RP={m.read_pointer} | WP={m.write_pointer} | FULL={int(m.full)} | EMPTY={int(m.empty)} | {m.depth}/{m.capacity}")
        occupied={(m.read_pointer+i)%m.capacity for i in range(m.depth)}
        self.cells.setRowCount(m.capacity)
        for i,v in enumerate(m.cells):
            state=self.t("Occupied","اشغال") if i in occupied else self.t("Unused","خالی")
            if i==m.read_pointer:state+=" · RP"
            if i==m.write_pointer:state+=" · WP"
            for col,val in enumerate((str(i),f"{v:04X}",state)):self.cells.setItem(i,col,QTableWidgetItem(val))
        self.result.setText(self.t("Queue head → tail","صف ابتدا به انتها")+": "+" ".join(f"{v:04X}" for v in m.contents()))

    def edge(self,read,write):
        try:e=self.model.edge(read,self.value.value() if write else None)
        except ValueError:
            self.status.setText(self.t("Overflow or underflow; no change.","سرریز یا کمبود؛ بدون تغییر."));return
        self.refresh()
        self.status.setText(("READ "+f"{e.read_value:04X}") if e.read_value is not None else "WRITE")
