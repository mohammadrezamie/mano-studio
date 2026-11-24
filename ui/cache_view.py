"""Interactive cache inspector, backed by real transactions and RAM."""
from PySide6.QtCore import Qt,QRectF
from PySide6.QtGui import QPainter,QColor,QPen,QFont
from PySide6.QtWidgets import (QWidget,QVBoxLayout,QHBoxLayout,QLabel,QComboBox,QSpinBox,
    QPushButton,QTableWidget,QTableWidgetItem,QHeaderView,QAbstractItemView,QSplitter)
from cache_model import Cache
from ui.theme import PALETTES


class CacheCanvas(QWidget):
    def __init__(self,view):
        super().__init__(view);self.view=view;self.setMinimumHeight(108)
        self.setAccessibleName(view.t("Cache address fields","فیلدهای آدرس حافظه نهان"))

    def paintEvent(self,event):
        v=self.view;m=v.model;e=v.last
        bg,panel,raised,fg,muted,accent,border=PALETTES[v.theme]
        p=QPainter(self);p.setRenderHint(QPainter.RenderHint.Antialiasing);p.fillRect(self.rect(),QColor(bg))
        scale=min(self.width()/780,self.height()/105)
        p.translate((self.width()-780*scale)/2,(self.height()-105*scale)/2);p.scale(scale,scale)
        index_bits=m.sets.bit_length()-1;tag_bits=8-index_bits
        addr=v.address.value()
        tag,index,offset=m.decode(addr)
        fields=((v.t("TAG","برچسب"),tag,tag_bits),(v.t("SET","مجموعه"),index,index_bits),(v.t("WORD OFFSET","جابه‌جایی کلمه"),offset,2))
        for i,(label,value,bits) in enumerate(fields):
            x=10+260*i
            p.setPen(QPen(QColor(accent if e and e.address==addr else border),1.5));p.setBrush(QColor(panel))
            p.drawRoundedRect(QRectF(x,8,240,68),8,8)
            font=QFont("Segoe UI");font.setPixelSize(13);p.setFont(font);p.setPen(QColor(muted))
            p.drawText(QRectF(x+10,13,220,20),Qt.AlignmentFlag.AlignCenter,label+f" · {bits} bit")
            font=QFont("Consolas");font.setPixelSize(23);font.setBold(True);p.setFont(font);p.setPen(QColor(fg))
            p.drawText(QRectF(x+10,35,220,32),Qt.AlignmentFlag.AlignCenter,f"{value:0{bits}b}" if bits else "—")
        p.setFont(QFont("Consolas",10));p.setPen(QColor(muted))
        p.drawText(QRectF(10,80,760,22),Qt.AlignmentFlag.AlignCenter,f"AR = {addr:010b}  /  {addr:03X}h")
        p.end()


class CacheView(QWidget):
    def __init__(self,theme="dark",fa=False):
        super().__init__();self.theme=theme;self.fa=fa;self.model=Cache();self.last=None
        layout=QVBoxLayout(self)
        note=QLabel(self.t("32 cached words · 4 words per block · 1024 × 16 backing RAM. Both write policies allocate on a miss. Traffic counts words, not clock cycles.",
          "۳۲ کلمه نهان · ۴ کلمه در هر بلوک · RAM با ۱۰۲۴ کلمه ۱۶ بیتی. هر دو سیاست نوشتن در صورت عدم اصابت تخصیص می‌دهند. شمارنده‌ها تعداد کلمات‌اند، نه چرخه ساعت."))
        note.setWordWrap(True);layout.addWidget(note)
        config=QHBoxLayout()
        self.ways=QComboBox()
        for n,en,fa_label in ((1,"Direct mapped","مستقیم"),(2,"2-way","دو راهه"),(4,"4-way","چهار راهه"),(8,"Fully associative","تمام‌انجمنی")):self.ways.addItem(self.t(en,fa_label),n)
        self.replacement=QComboBox();self.replacement.addItem("LRU","lru");self.replacement.addItem("FIFO","fifo")
        self.policy=QComboBox();self.policy.addItem(self.t("Write-back","نوشتن بازگشتی"),"back");self.policy.addItem(self.t("Write-through","نوشتن هم‌زمان"),"through")
        for widget in (self.ways,self.replacement,self.policy):config.addWidget(widget);widget.currentIndexChanged.connect(self.reset)
        b=QPushButton(self.t("Reset all","بازنشانی کامل"));b.clicked.connect(self.reset);config.addWidget(b)
        layout.addLayout(config)
        row=QHBoxLayout();self.address=QSpinBox();self.address.setRange(0,1023);self.address.setDisplayIntegerBase(16)
        self.value=QSpinBox();self.value.setRange(0,65535);self.value.setDisplayIntegerBase(16)
        row.addWidget(QLabel("AR HEX"));row.addWidget(self.address);row.addWidget(QLabel("DATA HEX"));row.addWidget(self.value)
        for en,fa_label,fn in (("Read","خواندن",lambda:self.access(False)),("Write","نوشتن",lambda:self.access(True)),("Flush dirty","تخلیه خطوط تغییریافته",self.flush),("Conflict demo","مثال تداخل",self.example)):
            b=QPushButton(self.t(en,fa_label));b.clicked.connect(fn);row.addWidget(b)
        layout.addLayout(row)
        self.canvas=CacheCanvas(self);layout.addWidget(self.canvas);self.address.valueChanged.connect(self.canvas.update)
        self.stats=QLabel();self.stats.setWordWrap(True);layout.addWidget(self.stats)
        split=QSplitter(Qt.Orientation.Vertical)
        self.lines=self.table(["SET","WAY","V","D","TAG","W0","W1","W2","W3","RAM W0–W3"])
        self.trace=self.table(["#","R/W","AR","TAG/SET/OFF",self.t("Result","نتیجه"),"WAY","DATA",self.t("Evicted block","بلوک حذف‌شده"),"RAM R/W"])
        split.addWidget(self.lines);split.addWidget(self.trace);layout.addWidget(split,1)
        self.status=QLabel();self.status.setWordWrap(True);layout.addWidget(self.status)
        self.reset()

    def t(self,en,fa):return fa if self.fa else en
    def table(self,headers):
        t=QTableWidget(0,len(headers));t.setHorizontalHeaderLabels(headers)
        t.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        t.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        t.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        t.horizontalHeader().setStretchLastSection(True);return t
    def reset(self,*_):
        # Changing configuration is a complete reset of this educational sandbox.
        self.model=Cache(self.ways.currentData(),self.replacement.currentData(),self.policy.currentData())
        self.last=None;self.trace.setRowCount(0)
        self.status.setText(self.t("Cache and backing RAM reset.","حافظه نهان و RAM بازنشانی شدند."));self.refresh()
    def refresh(self):
        m=self.model
        rate=100*m.hits/m.accesses if m.accesses else 0
        self.stats.setText(f"HIT {m.hits}   ·   MISS {m.misses}   ·   {rate:.1f}%   |   RAM R {m.ram_reads} / W {m.ram_writes}")
        self.lines.setRowCount(8)
        for index,ways in enumerate(m.lines):
            for way,line in enumerate(ways):
                valid=line.tag is not None
                base=(line.tag*m.sets+index)*4 if valid else None
                data=tuple(f"{v:04X}" for v in line.data) if valid else ("—",)*4
                ram=" ".join(f"{m.memory.read(base+i):04X}" for i in range(4)) if valid else "—"
                values=(index,way,int(valid),int(line.dirty),f"{line.tag:X}" if valid else "—",*data,ram)
                for col,value in enumerate(values):
                    item=QTableWidgetItem(str(value))
                    if self.last and (index,way)==(self.last.index,self.last.way):item.setBackground(QColor(PALETTES[self.theme][2]))
                    self.lines.setItem(index*m.ways+way,col,item)
        self.canvas.update()
    def access(self,write=False):
        e=self.last=self.model.access(self.address.value(),self.value.value() if write else None)
        result="HIT" if e.hit else "MISS"
        values=(e.number,"W" if write else "R",f"{e.address:03X}",f"{e.tag:X}/{e.index:X}/{e.offset}",result,e.way,f"{e.value:04X}",
                "—" if e.evicted_block is None else f"{e.evicted_block:02X}"+(" WB" if e.written_back else ""),f"{e.ram_reads}/{e.ram_writes}")
        if self.trace.rowCount()>=512:self.trace.removeRow(0)
        row=self.trace.rowCount();self.trace.insertRow(row)
        for i,value in enumerate(values):self.trace.setItem(row,i,QTableWidgetItem(str(value)))
        self.trace.scrollToBottom();self.status.setText(result);self.refresh()
    def flush(self):
        count=self.model.flush()
        self.status.setText(self.t("Words written to RAM: ","کلمات نوشته‌شده در RAM: ")+str(count));self.refresh()
    def example(self):
        self.reset()
        for address in (0,32,0,32,1,33):
            self.address.setValue(address);self.access(False)
