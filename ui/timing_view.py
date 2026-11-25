"""Independent timing exercise; does not change the live clocked model."""
from PySide6.QtCore import Qt,QPointF,QRectF
from PySide6.QtGui import QColor,QPainter,QPen
from PySide6.QtWidgets import QWidget,QVBoxLayout,QGridLayout,QLabel,QSpinBox,QPushButton
from timing_constraints import check
from ui.theme import PALETTES


class TimingDiagram(QWidget):
    def __init__(self,view,theme):
        super().__init__(view)
        self.view,self.theme=view,theme
        self.setMinimumHeight(150)
        self.setLayoutDirection(Qt.LayoutDirection.LeftToRight)

    def paintEvent(self,event):
        p=QPainter(self)
        bg,panel,raised,fg,muted,accent,border=PALETTES[self.theme]
        p.fillRect(self.rect(),QColor(bg))
        if self.view.result is None:
            p.end()
            return
        rise,fall,edge,setup,hold=self.view.values()
        end=max(30,edge+hold+1,fall+1)
        x=lambda t:44+(self.width()-60)*t/end
        p.setPen(QPen(QColor(muted),1))
        p.drawText(8,35,"D");p.drawText(8,100,"CLK")
        for start,stop in ((max(0,edge-setup),edge),(edge,edge+hold)):
            color=QColor(accent);color.setAlpha(42)
            p.fillRect(QRectF(x(start),14,x(stop)-x(start),105),color)
        def line(a,b,c,d,color=fg,width=2):
            p.setPen(QPen(QColor(color),width))
            p.drawLine(QPointF(a,b),QPointF(c,d))
        line(x(0),57,x(rise),57)
        line(x(rise),57,x(rise),25)
        line(x(rise),25,x(fall),25)
        line(x(fall),25,x(fall),57)
        line(x(fall),57,x(end),57)
        line(x(0),110,x(edge),110,accent)
        line(x(edge),110,x(edge),78,accent)
        line(x(edge),78,x(end),78,accent)
        line(x(edge),14,x(edge),119,muted,1)
        p.setPen(QColor(fg))
        p.drawText(QRectF(x(edge)-22,120,44,22),Qt.AlignmentFlag.AlignCenter,str(edge))
        p.end()


class TimingView(QWidget):
    def __init__(self,theme,fa=False):
        super().__init__()
        self.fa=fa
        self.result=None
        layout=QVBoxLayout(self)
        note=QLabel(self.t("A single D pulse and rising clock edge. Shaded windows must remain stable; exact boundary changes are allowed. This is an ideal constraint exercise, not analog metastability.",
            "یک پالس D و لبه بالارونده ساعت. در بازه‌های رنگی داده باید ثابت بماند؛ تغییر دقیقاً در مرز مجاز است. این تمرین ایده‌آل است، نه شبیه‌سازی متاپایداری."))
        note.setWordWrap(True)
        layout.addWidget(note)
        grid=QGridLayout()
        self.fields=[]
        for i,(en,fa_label,default) in enumerate((("D rise","بالاروی D",7),("D fall","پایین‌روی D",12),("Clock edge","لبه ساعت",10),("Setup","آماده‌سازی",3),("Hold","نگهداری",2))):
            field=QSpinBox()
            field.setRange(0,30)
            field.setValue(default)
            label=QLabel(self.t(en,fa_label))
            label.setBuddy(field)
            field.setAccessibleName(label.text())
            self.fields.append(field)
            grid.addWidget(label,i//3,(i%3)*2)
            grid.addWidget(field,i//3,(i%3)*2+1)
        layout.addLayout(grid)
        self.diagram=TimingDiagram(self,theme)
        layout.addWidget(self.diagram,1)
        self.status=QLabel()
        self.status.setWordWrap(True)
        layout.addWidget(self.status)
        example=QPushButton(self.t("Violation example","مثال نقض زمان‌بندی"))
        example.clicked.connect(self.example)
        layout.addWidget(example)
        for field in self.fields:
            field.valueChanged.connect(self.refresh)
        self.refresh()

    def t(self,en,fa):
        return fa if self.fa else en

    def values(self):
        return tuple(field.value() for field in self.fields)

    def example(self):
        for field,value in zip(self.fields,(8,11,10,3,2)):
            field.setValue(value)
        self.refresh()

    def refresh(self,*_):
        rise,fall,edge,setup,hold=self.values()
        if rise>=fall:
            self.result=None
            self.status.setText(self.t("D rise must precede D fall.","بالاروی D باید پیش از پایین‌روی باشد."))
        else:
            self.result=check(0,((rise,1),(fall,0)),edge,setup,hold)
            r=self.result
            if r.valid:
                self.status.setText(self.t("Constraints satisfied. Sampled D = ","شرط‌ها برقرارند. نمونه D = ")+str(r.sampled))
            else:
                parts=[]
                if r.setup_violations:
                    parts.append(self.t("Setup violation","نقض آماده‌سازی")+": "+", ".join(map(str,r.setup_violations)))
                if r.hold_violations:
                    parts.append(self.t("Hold violation","نقض نگهداری")+": "+", ".join(map(str,r.hold_violations)))
                if r.coincident:
                    parts.append(self.t("Coincident transition","تغییر هم‌زمان"))
                self.status.setText(" · ".join(parts)+"\n"+self.t("Sampled Q is not predicted.","حالت Q پیش‌بینی نمی‌شود."))
        self.diagram.update()
