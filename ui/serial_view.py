"""Live TX/RX bit slots and receive queue in the existing I/O inspector."""
from PySide6.QtCore import Qt,QRectF,QPointF,QTimer,QSignalBlocker
from PySide6.QtGui import QPainter,QColor,QPen,QFont,QPainterPath
from PySide6.QtWidgets import (QWidget,QVBoxLayout,QHBoxLayout,QLabel,QComboBox,QSpinBox,
    QPushButton,QTableWidget,QTableWidgetItem,QHeaderView,QAbstractItemView)
from serial_io import Format,SerialLink
from ui.theme import PALETTES


class SerialCanvas(QWidget):
    def __init__(self,view):
        super().__init__(view);self.view=view
        self.setMinimumHeight(210)
        self.setAccessibleName(view.t("Transmitted and received serial frame","فریم سریال ارسالی و دریافتی"))

    def paintEvent(self,event):
        v=self.view;m=v.model
        bg,panel,raised,fg,muted,accent,border=PALETTES[v.theme]
        p=QPainter(self);p.setRenderHint(QPainter.RenderHint.Antialiasing);p.fillRect(self.rect(),QColor(bg))
        left=62;right=max(left+1,self.width()-14);n=len(m.format.labels);dx=(right-left)/n
        bad=("#a62f36" if v.theme=="light" else "#ffb5ab")
        p.setFont(QFont("Consolas",10))
        for i,label in enumerate(m.format.labels):
            x=left+i*dx
            sent=i<len(m.rx)
            changed=sent and m.rx[i]!=m.tx[i]
            current=sent and i==len(m.rx)-1
            shade=QColor(bad if changed else accent);shade.setAlpha(35 if current or changed else 0)
            if current or changed:p.fillRect(QRectF(x,4,dx,166),shade)
            p.setPen(QPen(QColor(bad if changed else border),1))
            p.drawLine(QPointF(x,4),QPointF(x,170))
            p.setPen(QColor(fg if sent else muted));p.drawText(QRectF(x,5,dx,24),Qt.AlignmentFlag.AlignCenter,label)
            if sent:p.drawText(QRectF(x,145,dx,20),Qt.AlignmentFlag.AlignCenter,f"{m.tx[i]} / {m.rx[i]}")
        for j,(name,bits) in enumerate((("TX",m.tx[:len(m.rx)]),("RX",tuple(m.rx)))):
            y=54+j*58
            p.setPen(QColor(fg));p.drawText(QRectF(8,y-16,48,34),Qt.AlignmentFlag.AlignCenter,name)
            p.setPen(QPen(QColor(border),1));p.drawLine(QPointF(left,y+15),QPointF(right,y+15))
            if bits:
                path=QPainterPath(QPointF(left,y+12-24*bits[0]))
                for i,bit in enumerate(bits):
                    level=y+12-24*bit;x=left+i*dx
                    path.lineTo(x,level);path.lineTo(x+dx,level)
                p.setPen(QPen(QColor(accent if j==0 else fg),2.5));p.drawPath(path)
        p.setPen(QColor(muted))
        p.drawText(QRectF(left,174,right-left,25),Qt.AlignmentFlag.AlignCenter,v.t("Completed bit slots · TX / RX · not physical time","بازه‌های بیت تکمیل‌شده · ارسال / دریافت · نه زمان فیزیکی"))
        p.end()


class SerialView(QWidget):
    def __init__(self,fa=False,notify=None,theme="dark"):
        super().__init__();self.fa=fa;self.notify=notify;self.theme=theme
        self.model=SerialLink(notify=notify)
        layout=QVBoxLayout(self)
        note=QLabel(self.t("Ideal aligned bit slots, LSB first. Corrupt one selected bit to test start, parity or stop checks. Only valid frames enter the shared FIFO model; completion notifies IRQ3.",
          "بازه‌های بیت هم‌تراز ایده‌آل، بیت کم‌ارزش اول. یک بیت را برای آزمون خطای شروع، توازن یا پایان تغییر دهید. فقط فریم معتبر وارد مدل FIFO می‌شود؛ پایان فریم IRQ3 را فعال می‌کند."))
        note.setWordWrap(True);layout.addWidget(note)
        row=QHBoxLayout();self.bits=QComboBox()
        for n in (5,6,7,8):self.bits.addItem(f"{n} "+self.t("bit","بیت"),n)
        self.bits.setCurrentIndex(3)
        self.parity=QComboBox()
        for en,fa_label,key in (("No parity","بدون توازن","none"),("Even","زوج","even"),("Odd","فرد","odd")):self.parity.addItem(self.t(en,fa_label),key)
        self.stops=QComboBox()
        for n in (1,2):self.stops.addItem(f"{n} "+self.t("stop bit","بیت پایان"),n)
        self.payload=QSpinBox();self.payload.setRange(0,255);self.payload.setDisplayIntegerBase(16);self.payload.setValue(0xA5);self.payload.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.flip=QComboBox()
        for widget in (self.bits,self.parity,self.stops):row.addWidget(widget);widget.currentIndexChanged.connect(self.configure)
        row.addWidget(QLabel("HEX"));row.addWidget(self.payload);row.addWidget(self.flip)
        layout.addLayout(row)
        row=QHBoxLayout()
        self.start_button=QPushButton(self.t("Load frame","بارگذاری فریم"));self.start_button.clicked.connect(self.start)
        self.step_button=QPushButton(self.t("Next bit","بیت بعد"));self.step_button.clicked.connect(self.step)
        self.run_button=QPushButton(self.t("Play frame","پخش فریم"));self.run_button.clicked.connect(self.play)
        self.finish_button=QPushButton(self.t("Finish now","تکمیل فوری"));self.finish_button.clicked.connect(self.finish)
        self.read_button=QPushButton(self.t("Read FIFO","خواندن FIFO"));self.read_button.clicked.connect(self.read)
        reset=QPushButton(self.t("Reset","بازنشانی"));reset.clicked.connect(self.configure)
        for b in (self.start_button,self.step_button,self.run_button,self.finish_button,self.read_button,reset):row.addWidget(b)
        layout.addLayout(row)
        self.canvas=SerialCanvas(self);layout.addWidget(self.canvas,1)
        self.status=QLabel();self.status.setWordWrap(True);layout.addWidget(self.status)
        self.queue=QLabel();self.queue.setWordWrap(True);layout.addWidget(self.queue)
        self.trace=QTableWidget(0,5);self.trace.setHorizontalHeaderLabels(["#",self.t("Slot","بازه"),"TX","RX","RX SHIFT"])
        self.trace.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.trace.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.trace.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.trace,1)
        self.timer=QTimer(self);self.timer.setInterval(250);self.timer.timeout.connect(self.step)
        self.configure()

    def t(self,en,fa):return fa if self.fa else en
    def configure(self,*_):
        self.timer.stop()
        fmt=Format(self.bits.currentData(),self.parity.currentData(),self.stops.currentData())
        self.model=SerialLink(fmt,notify=self.notify)
        self.payload.setMaximum((1<<fmt.data_bits)-1)
        with QSignalBlocker(self.flip):
            self.flip.clear();self.flip.addItem(self.t("No corruption","بدون خطا"),None)
            for i,label in enumerate(fmt.labels):self.flip.addItem(self.t("Flip ","تغییر ")+label,i)
        self.trace.setRowCount(0);self.refresh()
    def start(self):
        if self.model.active:return
        self.model.start(self.payload.value(),self.flip.currentData());self.trace.setRowCount(0);self.refresh()
    def step(self):
        e=self.model.step()
        if e is not None:
            row=self.trace.rowCount();self.trace.insertRow(row)
            for i,value in enumerate((e.index,e.label,e.tx,e.rx,f"{e.shift:02X}")):self.trace.setItem(row,i,QTableWidgetItem(str(value)))
            self.trace.scrollToBottom()
        if not self.model.active:self.timer.stop()
        self.refresh()
    def play(self):
        if self.timer.isActive():self.timer.stop()
        elif self.model.active and self.isVisible():self.timer.start()
        self.refresh()
    def finish(self):
        self.timer.stop()
        while self.model.active:self.step()
    def read(self):
        if not self.model.fifo.empty:
            value=self.model.read();self.refresh()
            self.status.setText(self.t("FIFO read: ","خواندن FIFO: ")+f"{value:02X}")
    def refresh(self):
        m=self.model
        active=m.active;playing=self.timer.isActive()
        self.start_button.setEnabled(not active);self.step_button.setEnabled(active and not playing)
        self.run_button.setEnabled(active);self.finish_button.setEnabled(active)
        self.run_button.setText(self.t("Pause","توقف موقت") if playing else self.t("Play frame","پخش فریم"))
        self.read_button.setEnabled(not m.fifo.empty)
        for w in (self.bits,self.parity,self.stops,self.payload,self.flip):w.setEnabled(not active)
        result=m.result
        if result is None:state=f"RX SHIFT = {m.shift:02X} · {len(m.rx)}/{len(m.tx)}"
        else:
            errors=[]
            if result.start_error:errors.append(self.t("Start error","خطای شروع"))
            if result.parity_error:errors.append(self.t("Parity error","خطای توازن"))
            if result.framing_error:errors.append(self.t("Stop error","خطای پایان"))
            if m.overrun:errors.append(self.t("FIFO overrun","سرریز FIFO"))
            state=f"RX {result.value:02X}  ·  "+(" / ".join(errors) if errors else self.t("Accepted","پذیرفته شد"))
        self.status.setText(state)
        self.queue.setText(f"FIFO {m.fifo.depth}/{m.fifo.capacity}  ·  "+" ".join(f"{w:02X}" for w in m.fifo.contents())+
          " | "+self.t("Frames","فریم‌ها")+f" {m.completed} · "+self.t("Errors","خطاها")+f" {m.errors} · "+self.t("Dropped","حذف‌شده")+f" {m.dropped}")
        self.canvas.update()
    def hideEvent(self,event):
        self.timer.stop();self.refresh();super().hideEvent(event)
