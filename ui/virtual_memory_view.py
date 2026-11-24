"""Chapter 12: live CAM search and paged address translation."""
from PySide6.QtCore import Qt,QRectF,QPointF
from PySide6.QtGui import QPainter,QColor,QPen,QFont
from PySide6.QtWidgets import (QWidget,QVBoxLayout,QHBoxLayout,QLabel,QComboBox,QSpinBox,
    QPushButton,QTableWidget,QTableWidgetItem,QHeaderView,QAbstractItemView,QSplitter)
from ui.motion import MotionTabs
from ui.theme import PALETTES
from associative_memory import AssociativeMemory
from virtual_memory import VirtualMemory


def spin(maximum):
    w=QSpinBox();w.setRange(0,maximum);w.setDisplayIntegerBase(16);return w


def table(headers):
    t=QTableWidget(0,len(headers));t.setHorizontalHeaderLabels(headers)
    t.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
    t.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
    t.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
    return t


def fill(t,rows,highlight=(),color=None):
    t.setRowCount(len(rows))
    for i,row in enumerate(rows):
        for j,value in enumerate(row):
            item=QTableWidgetItem(str(value))
            if i in highlight and color:item.setBackground(QColor(color))
            t.setItem(i,j,item)


class CAMView(QWidget):
    def __init__(self,theme,fa):
        super().__init__();self.theme=theme;self.fa=fa;self.model=AssociativeMemory()
        layout=QVBoxLayout(self)
        note=QLabel(self.t("8 × 8 content-addressable memory. Mask 1 compares a bit; mask 0 ignores it. All valid matches are shown; lowest row wins the priority encoder.",
                         "حافظه انجمنی ۸×۸. بیت ۱ ماسک مقایسه می‌شود و بیت ۰ نادیده گرفته می‌شود. همه تطابق‌های معتبر نمایش داده می‌شوند؛ کمترین شماره ردیف در انکدر اولویت دارد."))
        note.setWordWrap(True);layout.addWidget(note)
        row=QHBoxLayout();self.row=spin(7);self.word=spin(255);self.key=spin(255);self.mask=spin(255);self.mask.setValue(255)
        for label,w in (("ROW",self.row),("DATA",self.word),("KEY",self.key),("MASK",self.mask)):
            row.addWidget(QLabel(label));row.addWidget(w)
        for en,fa_label,fn in (("Write","نوشتن",self.write),("Invalidate","نامعتبر",self.invalidate),("Example","مثال",self.example)):
            button=QPushButton(self.t(en,fa_label));button.clicked.connect(fn);row.addWidget(button)
        layout.addLayout(row)
        self.result=QLabel();self.result.setWordWrap(True);layout.addWidget(self.result)
        self.rows=table(["ROW","V","DATA","b7…b0","XOR & MASK","MATCH"]);layout.addWidget(self.rows,1)
        self.key.valueChanged.connect(self.refresh);self.mask.valueChanged.connect(self.refresh)
        self.example()

    def t(self,en,fa):return fa if self.fa else en
    def example(self):
        self.model=AssociativeMemory()
        for i,w in enumerate((0xA1,0xA5,0xB1,0xA0,0x05,0xFF)):self.model.write(i,w)
        self.key.setValue(0xA0);self.mask.setValue(0xF0);self.refresh()
    def write(self):
        self.model.write(self.row.value(),self.word.value());self.refresh()
    def invalidate(self):
        self.model.invalidate(self.row.value());self.refresh()
    def refresh(self,*_):
        key,mask=self.key.value(),self.mask.value()
        self.match=self.model.search(key,mask)
        rows=[]
        for i,w in enumerate(self.model.words):
            rows.append((i,int(w is not None),"—" if w is None else f"{w:02X}","—" if w is None else f"{w:08b}",
                         "—" if w is None else f"{(w^key)&mask:08b}",int(i in self.match.matches)))
        fill(self.rows,rows,self.match.matches,PALETTES[self.theme][2])
        self.result.setText(f"KEY {key:08b}   ·   MASK {mask:08b}   |   MATCH "+", ".join(map(str,self.match.matches))+
                            "   |   PRIORITY "+("—" if self.match.first is None else str(self.match.first)))


class TranslationCanvas(QWidget):
    def __init__(self,view):
        super().__init__(view);self.view=view;self.setMinimumHeight(125)
        self.setAccessibleName(view.t("Virtual to physical address path","مسیر آدرس مجازی به فیزیکی"))
    def paintEvent(self,event):
        v=self.view;e=v.last
        bg,panel,raised,fg,muted,accent,border=PALETTES[v.theme]
        p=QPainter(self);p.setRenderHint(QPainter.RenderHint.Antialiasing);p.fillRect(self.rect(),QColor(bg))
        scale=min(self.width()/800,self.height()/125)
        p.translate((self.width()-800*scale)/2,(self.height()-125*scale)/2);p.scale(scale,scale)
        stages=(("VA / VPN + OFF","—" if e is None else f"{e.virtual:02X} / {e.vpn:X} + {e.offset:X}"),
                ("TLB","—" if e is None else "HIT" if e.tlb_hit else "MISS"),
                ("PAGE TABLE","—" if e is None else "FAULT" if e.fault else f"FRAME {e.frame}"),
                ("PA / DATA","—" if e is None else f"{e.physical:02X} / {e.value:04X}"))
        for i,(name,value) in enumerate(stages):
            x=10+i*200
            p.setPen(QPen(QColor(accent if e else border),1.5));p.setBrush(QColor(panel))
            p.drawRoundedRect(QRectF(x,14,180,79),10,10)
            font=QFont("Consolas");font.setPixelSize(13);p.setFont(font);p.setPen(QColor(muted))
            p.drawText(QRectF(x,20,180,23),Qt.AlignmentFlag.AlignCenter,name)
            font.setPixelSize(18);font.setBold(True);p.setFont(font);p.setPen(QColor(fg))
            p.drawText(QRectF(x,45,180,38),Qt.AlignmentFlag.AlignCenter,value)
            if i<3:
                p.setPen(QPen(QColor(accent if e else border),2))
                p.drawLine(QPointF(x+180,54),QPointF(x+200,54))
        p.end()


class PagingView(QWidget):
    def __init__(self,theme,fa):
        super().__init__();self.theme=theme;self.fa=fa;self.last=None
        layout=QVBoxLayout(self)
        note=QLabel(self.t("256 virtual words · 64 physical words · 16 words/page. Faults load pages from simulated backing storage. No physical timing or real OS.",
          "۲۵۶ کلمه مجازی · ۶۴ کلمه فیزیکی · ۱۶ کلمه در صفحه. خطای صفحه از حافظه پشتیبان شبیه‌سازی‌شده بارگذاری می‌کند. بدون زمان‌بندی فیزیکی یا سیستم‌عامل واقعی."))
        note.setWordWrap(True);layout.addWidget(note)
        row=QHBoxLayout();self.replacement=QComboBox();self.replacement.addItem("LRU","lru");self.replacement.addItem("FIFO","fifo")
        self.tlb_size=QComboBox()
        for n in (2,4):self.tlb_size.addItem(f"TLB {n}",n)
        row.addWidget(self.replacement);row.addWidget(self.tlb_size)
        self.address=spin(255);self.value=spin(65535)
        row.addWidget(QLabel("VA HEX"));row.addWidget(self.address);row.addWidget(QLabel("DATA HEX"));row.addWidget(self.value)
        for en,fa_label,fn in (("Read","خواندن",lambda:self.access(False)),("Write","نوشتن",lambda:self.access(True)),
                               ("Demo","مثال",self.example),("Reset","بازنشانی",self.reset)):
            b=QPushButton(self.t(en,fa_label));b.clicked.connect(fn);row.addWidget(b)
        layout.addLayout(row)
        self.canvas=TranslationCanvas(self);layout.addWidget(self.canvas)
        self.stats=QLabel();self.stats.setWordWrap(True);layout.addWidget(self.stats)
        split=QSplitter(Qt.Orientation.Horizontal)
        self.pages=table(["VPN","V","PFN","D"]);self.frames=table(["PFN","VPN","DATA[0]","DATA[1]"])
        self.tlb=table(["VPN","PFN"])
        split.addWidget(self.pages);split.addWidget(self.frames);split.addWidget(self.tlb);layout.addWidget(split,1)
        self.trace=table(["#","VA","TLB","FAULT","PA","DATA","EVICT","WB"]);layout.addWidget(self.trace,1)
        self.replacement.currentIndexChanged.connect(self.reset);self.tlb_size.currentIndexChanged.connect(self.reset)
        self.reset()

    def t(self,en,fa):return fa if self.fa else en
    def reset(self,*_):
        self.model=VirtualMemory(self.replacement.currentData(),self.tlb_size.currentData())
        self.last=None;self.trace.setRowCount(0);self.refresh()
    def refresh(self):
        m=self.model;e=self.last;c=PALETTES[self.theme][2]
        self.stats.setText(f"TLB HIT {m.hits}/{m.accesses}   |   FAULT {m.faults}   |   PAGE IN {m.page_ins} / OUT {m.page_outs}")
        fill(self.pages,[(f"{i:X}",int(p.frame is not None),"—" if p.frame is None else p.frame,int(p.dirty)) for i,p in enumerate(m.pages)],(e.vpn,) if e else (),c)
        fill(self.frames,[(i,"—" if owner is None else f"{owner:X}",f"{m.ram.read(i*16):04X}",f"{m.ram.read(i*16+1):04X}") for i,owner in enumerate(m.owners)],(e.frame,) if e else (),c)
        fill(self.tlb,[(f"{vpn:X}",frame) for vpn,frame in m.tlb.items()])
        self.canvas.update()
    def access(self,write):
        e=self.last=self.model.access(self.address.value(),self.value.value() if write else None)
        if self.trace.rowCount()>=512:self.trace.removeRow(0)
        row=self.trace.rowCount();self.trace.insertRow(row)
        values=(e.number,f"{e.virtual:02X}","HIT" if e.tlb_hit else "MISS",int(e.fault),f"{e.physical:02X}",f"{e.value:04X}","—" if e.evicted is None else f"{e.evicted:X}",int(e.written_back))
        for i,x in enumerate(values):self.trace.setItem(row,i,QTableWidgetItem(str(x)))
        self.trace.scrollToBottom();self.refresh()
    def example(self):
        self.reset()
        self.address.setValue(0);self.value.setValue(0xCAFE);self.access(True)
        for address in (1,16,32,48,64,0):self.address.setValue(address);self.access(False)


class AddressTranslationView(QWidget):
    def __init__(self,theme,fa):
        super().__init__()
        layout=QVBoxLayout(self);self.tabs=MotionTabs();layout.addWidget(self.tabs)
        self.cam=CAMView(theme,fa);self.paging=PagingView(theme,fa)
        self.tabs.addTab(self.cam,"حافظه انجمنی" if fa else "Associative memory")
        self.tabs.addTab(self.paging,"حافظه مجازی / TLB" if fa else "Virtual memory / TLB")
