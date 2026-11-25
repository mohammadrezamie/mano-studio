"""Interactive Omega network; reservations come only from omega_network."""
from PySide6.QtCore import Qt, QPointF, QRectF
from PySide6.QtGui import QPainter, QPen, QColor, QFont
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QComboBox, QSpinBox, QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QAbstractItemView)
from omega_network import transfer_round
from ui.theme import PALETTES


class OmegaCanvas(QWidget):
    def __init__(self, view):
        super().__init__(view)
        self.view = view
        self.setMinimumHeight(230)
        self.setAccessibleName(view.t("Omega switch network", "شبکه سوئیچ امگا"))

    def paintEvent(self, event):
        v = self.view
        n = v.size.currentData()
        stages = n.bit_length() - 1
        bg, panel, raised, fg, muted, accent, border = PALETTES[v.theme]
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.fillRect(self.rect(), QColor(bg))
        w, h = self.width(), self.height()
        dy = (h - 48) / n
        dx = (w - 100) / stages
        def y(i):
            return 28 + (i + .5) * dy
        def x(s):
            return 50 + s * dx
        sw = min(32, dx * .36)
        def line(x1,y1,x2,y2,color=border,width=1):
            p.setPen(QPen(QColor(color),width))
            p.drawLine(QPointF(x1,y1),QPointF(x2,y2))
        font = QFont()
        font.setPixelSize(10)
        p.setFont(font)
        for s in range(stages):
            p.setPen(QColor(fg))
            p.drawText(QRectF(x(s),2,dx,22),Qt.AlignmentFlag.AlignCenter,f"S{s}")
            for i in range(0,n,2):
                p.setPen(QPen(QColor(border)))
                p.setBrush(QColor(panel))
                p.drawRoundedRect(QRectF(x(s),y(i)-dy*.38,sw,dy*1.76),3,3)
            for i in range(n):
                if s == 0:
                    line(25,y(i),x(s),y(i))
                if s == stages-1:
                    line(x(s)+sw,y(i),w-26,y(i))
                else:
                    j = ((i<<1)&(n-1)) | (i>>(stages-1))
                    line(x(s)+sw,y(i),x(s+1),y(j))
        for i in range(n):
            p.setPen(QColor(muted))
            p.drawText(QRectF(0,y(i)-7,24,14),Qt.AlignmentFlag.AlignCenter,f"P{i}")
            p.drawText(QRectF(w-26,y(i)-7,26,14),Qt.AlignmentFlag.AlignCenter,f"D{i}")
        for t in v.results:
            if not t.granted:
                continue
            for s, hop in enumerate(t.hops):
                line(x(s),y(hop.input_line),x(s)+sw,y(hop.output_line),accent,2)
                if s+1 < stages:
                    line(x(s)+sw,y(hop.output_line),x(s+1),y(t.hops[s+1].input_line),accent,2)
            line(25,y(t.source),x(0),y(t.source),accent,2)
            line(x(stages-1)+sw,y(t.destination),w-26,y(t.destination),accent,2)
        p.end()


class OmegaView(QWidget):
    def __init__(self, theme="dark", fa=False):
        super().__init__()
        self.theme, self.fa = theme, fa
        self.requests = {}
        self.results = ()
        layout = QVBoxLayout(self)
        note = QLabel(self.t("Unique destination-bit routes, perfect-shuffle wiring and fixed source priority. Distinct destinations can still block internally.",
            "مسیر یکتا با بیت‌های مقصد، سیم‌بندی درهم‌ریزی کامل و اولویت ثابت مبدأ. حتی مقصدهای متفاوت ممکن است درون شبکه تداخل کنند."))
        note.setWordWrap(True)
        layout.addWidget(note)
        row = QHBoxLayout()
        self.size = QComboBox()
        for n in (2,4,8,16):
            self.size.addItem(f"{n} × {n}",n)
        self.size.setCurrentIndex(2)
        self.source, self.destination = QSpinBox(), QSpinBox()
        for label, widget in ((self.t("Ports","پورت‌ها"),self.size),(self.t("Source","مبدأ"),self.source),(self.t("Destination","مقصد"),self.destination)):
            caption = QLabel(label)
            caption.setBuddy(widget)
            widget.setAccessibleName(label)
            widget.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
            row.addWidget(caption)
            row.addWidget(widget)
        layout.addLayout(row)
        row = QHBoxLayout()
        for en, fa_label, fn in (("Set request","ثبت درخواست",self.set_request),
            ("Remove","حذف",self.remove),("Run round","اجرای دور",self.run),
            ("Example","مثال",self.example),("Reset","بازنشانی",self.reset)):
            button = QPushButton(self.t(en,fa_label))
            button.clicked.connect(fn)
            row.addWidget(button)
        layout.addLayout(row)
        self.canvas = OmegaCanvas(self)
        layout.addWidget(self.canvas,2)
        self.status = QLabel()
        self.status.setWordWrap(True)
        layout.addWidget(self.status)
        self.table = QTableWidget(0,5)
        self.table.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setHorizontalHeaderLabels([self.t("Source","مبدأ"),self.t("Destination","مقصد"),
            self.t("Result","نتیجه"),self.t("Path outputs","خروجی مسیر"),self.t("Conflict","تداخل")])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table,1)
        self.size.currentIndexChanged.connect(self.reset)
        self.reset()

    def t(self,en,fa):
        return fa if self.fa else en

    def reset(self,*_):
        self.requests = {}
        self.results = ()
        for field in (self.source,self.destination):
            field.setRange(0,self.size.currentData()-1)
            field.setValue(0)
        self.refresh()

    def set_request(self):
        self.requests[self.source.value()] = self.destination.value()
        self.results = ()
        self.refresh()

    def remove(self):
        self.requests.pop(self.source.value(),None)
        self.results = ()
        self.refresh()

    def run(self):
        self.results = transfer_round(self.size.currentData(),self.requests.items())
        self.refresh()

    def example(self):
        self.reset()
        n = self.size.currentData()
        self.requests = {0:0,1:1} if n>2 else {0:1,1:0}
        self.run()

    def refresh(self):
        results = {t.source:t for t in self.results}
        self.table.setRowCount(len(self.requests))
        for row,(source,dest) in enumerate(sorted(self.requests.items())):
            t = results.get(source)
            status = self.t("Pending","در انتظار") if t is None else (self.t("Granted","مجاز") if t.granted else self.t("Blocked","مسدود"))
            path = "—" if t is None else " → ".join(str(h.output_line) for h in t.hops)
            conflict = "—" if t is None or t.granted else f"S{t.blocked_stage} / P{t.blocked_by}"
            for col,value in enumerate((str(source),str(dest),status,path,conflict)):
                item = QTableWidgetItem(value)
                item.setToolTip(value)
                self.table.setItem(row,col,item)
        self.status.setText(self.t("Requests","درخواست‌ها")+f": {len(self.requests)}  ·  "+
            self.t("Granted","مجاز")+f": {sum(t.granted for t in self.results)}  ·  "+
            self.t("Blocked","مسدود")+f": {sum(not t.granted for t in self.results)}")
        self.canvas.update()
