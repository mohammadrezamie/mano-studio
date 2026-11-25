"""Embedded clocked-component workbench with sample-based waveform view."""
from PySide6.QtCore import Qt, QRectF, QPointF, Signal, QSignalBlocker
from PySide6.QtGui import QColor,QPainter,QPen,QFont,QPainterPath
from PySide6.QtWidgets import QWidget,QVBoxLayout,QHBoxLayout,QGridLayout,QComboBox,QLabel,QPushButton,QSlider,QCheckBox,QFileDialog
from sequential_logic import ClockedCircuit, MODELS, RULES
from ui.theme import PALETTES
from waveform_analysis import recorded,window,write_csv
from ui.motion import MotionTabs
from ui.flipflop_reference_view import FlipFlopReferenceView
from ui.timing_view import TimingView

TITLES={
    "D":("D flip-flop","فلیپ‌فلاپ D"),
    "JK":("JK flip-flop","فلیپ‌فلاپ JK"),
    "T":("T flip-flop","فلیپ‌فلاپ T"),
    "SR":("Clocked SR flip-flop","فلیپ‌فلاپ SR ساعت‌دار"),
    "REG4":("4-bit register","ثبات ۴ بیتی"),
    "COUNT4":("4-bit up counter","شمارنده صعودی ۴ بیتی"),
    "SHIFT4":("4-bit serial shift register","ثبات شیفت سری ۴ بیتی"),
    "UNIVERSAL4":("4-bit universal shift register","ثبات شیفت عمومی ۴ بیتی"),
    "UPDOWN4":("4-bit loadable up/down counter","شمارنده صعودی/نزولی بارپذیر ۴ بیتی"),
    "RING4":("4-stage ring counter","شمارنده حلقوی ۴ مرحله‌ای"),
    "JOHNSON4":("4-stage Johnson counter","شمارنده جانسون ۴ مرحله‌ای"),
}


class ClockedDiagram(QWidget):
    def __init__(self, theme):
        super().__init__()
        self.theme=theme
        self.model=None
        self.setMinimumHeight(155)

    def paintEvent(self,event):
        if self.model is None:
            return
        p=QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        bg,panel,raised,fg,muted,accent,border=PALETTES[self.theme]
        p.fillRect(self.rect(),QColor(bg))
        m=self.model
        inputs=list(m.inputs.items())+[("CLK",m.clock)]
        outputs=list(m.outputs.items())
        design_height=max(205,75+24*max(len(inputs),len(outputs)))
        scale=min(self.width()/640,self.height()/design_height)
        p.translate((self.width()-640*scale)/2,(self.height()-design_height*scale)/2)
        p.scale(scale,scale)
        body=QRectF(238,14,164,design_height-30)
        p.setBrush(QColor(panel))
        p.setPen(QPen(QColor(fg),1.5))
        p.drawRect(body)
        p.setFont(QFont("Segoe UI",12,QFont.Weight.Bold))
        p.drawText(QRectF(238,14,164,27),Qt.AlignmentFlag.AlignCenter,m.kind)
        p.setFont(QFont("Consolas",11))
        for i,(name,value) in enumerate(inputs):
            y=51+i*24
            color=QColor(accent if value else muted)
            p.setPen(QPen(color,2 if value else 1))
            p.drawLine(QPointF(160,y),QPointF(238,y))
            p.drawText(QRectF(80,y-10,70,20),Qt.AlignmentFlag.AlignRight,f"{name} {value}")
            if name=="CLK":
                path=QPainterPath(QPointF(238,y-7))
                path.lineTo(250,y)
                path.lineTo(238,y+7)
                p.setPen(QPen(QColor(fg),1.5))
                p.drawPath(path)
            else:
                p.setPen(QColor(fg))
                p.drawText(QRectF(245,y-10,70,20),Qt.AlignmentFlag.AlignLeft,name)
        for i,(name,value) in enumerate(outputs):
            name = "Q\u0305" if name=="Qbar" else name
            y=51+i*24
            color=QColor(accent if value else muted)
            p.setPen(QPen(color,2 if value else 1))
            p.drawLine(QPointF(402,y),QPointF(480,y))
            p.drawText(QRectF(490,y-10,80,20),Qt.AlignmentFlag.AlignLeft,f"{name} {value}")
            p.setPen(QColor(fg))
            p.drawText(QRectF(325,y-10,70,20),Qt.AlignmentFlag.AlignRight,name)
        p.end()


class WaveformView(QWidget):
    selected=Signal(int)

    def __init__(self, theme, fa=False):
        super().__init__()
        self.theme=theme;self.model=None;self.rows=();self.names=();self.cursor=None
        self.fa=fa
        self.setMinimumHeight(300)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setAccessibleName("تاریخچه نمودار زمانی" if fa else "Digital waveform history")
        self.setToolTip("Click a sample or use Left/Right/Home/End" if not fa else "نمونه را انتخاب کنید یا از کلیدهای جهت، Home و End استفاده کنید")

    def set_window(self,names,rows,cursor=None):
        self.names,self.rows=names,rows
        self.cursor=cursor if any(r.number==cursor for r in rows) else None
        self.update()

    def geometry_values(self):
        left=76;right=max(left+1,self.width()-16)
        return left,right,(right-left)/max(1,len(self.rows))

    def choose(self,number):
        if any(r.number==number for r in self.rows):
            self.cursor=number;self.selected.emit(number);self.update()

    def mousePressEvent(self,event):
        left,right,spacing=self.geometry_values()
        x=event.position().x()
        if self.rows and left<=x<=right:
            self.choose(self.rows[min(len(self.rows)-1,int((x-left)/spacing))].number)
            self.setFocus()
        super().mousePressEvent(event)

    def keyPressEvent(self,event):
        if self.rows and event.key() in (Qt.Key.Key_Left,Qt.Key.Key_Right,Qt.Key.Key_Home,Qt.Key.Key_End):
            lo,hi=self.rows[0].number,self.rows[-1].number
            current=self.cursor if self.cursor is not None else hi
            number={Qt.Key.Key_Left:max(lo,current-1),Qt.Key.Key_Right:min(hi,current+1),
                    Qt.Key.Key_Home:lo,Qt.Key.Key_End:hi}[event.key()]
            self.choose(number);event.accept();return
        super().keyPressEvent(event)

    def paintEvent(self,event):
        p=QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        bg,panel,raised,fg,muted,accent,border=PALETTES[self.theme]
        p.fillRect(self.rect(),QColor(bg))
        names,rows=self.names,self.rows
        if not rows or not names:p.end();return
        left,right,spacing=self.geometry_values()
        top=25
        pitch=max(12,(self.height()-top-27)/len(names))
        bottom=top+len(names)*pitch
        p.setFont(QFont("Consolas",9))
        # Highlight recorded rising edges, not inferred physical timing.
        for j,r in enumerate(rows):
            x=left+j*spacing
            if r.number==self.cursor:
                shade=QColor(accent);shade.setAlpha(30)
                p.fillRect(QRectF(x,top,spacing,bottom-top),shade)
            p.setPen(QPen(QColor(accent if r.rising else border),1,Qt.PenStyle.DashLine if r.rising else Qt.PenStyle.SolidLine))
            p.drawLine(QPointF(x,top),QPointF(x,bottom))
            if j==0 or j==len(rows)-1 or (spacing>=27 and j%2==0):
                p.setPen(QColor(muted))
                p.drawText(QRectF(x,3,max(spacing,22),18),Qt.AlignmentFlag.AlignLeft,str(r.number))
        for i,name in enumerate(names):
            y=top+i*pitch
            p.fillRect(QRectF(4,y,left-8,pitch-2),QColor(panel if i%2==0 else raised))
            p.setPen(QColor(fg))
            p.drawText(QRectF(10,y,left-15,pitch),Qt.AlignmentFlag.AlignVCenter,"Q\u0305" if name=="Qbar" else name)
            p.setPen(QPen(QColor(border),1))
            p.drawLine(QPointF(left,y+pitch-1),QPointF(right,y+pitch-1))
            height=min(14,pitch*.49)
            def level(value):return y+pitch*.76-height*value
            path=QPainterPath(QPointF(left,level(rows[0].values[i])))
            for j,sample in enumerate(rows):
                x=left+j*spacing
                path.lineTo(x,level(sample.values[i]))
                path.lineTo(x+spacing,level(sample.values[i]))
            p.setPen(QPen(QColor(accent if i==0 else fg),1.8))
            p.drawPath(path)
        if self.cursor is not None:
            x=left+(self.cursor-rows[0].number+.5)*spacing
            p.setPen(QPen(QColor(accent),1.6))
            p.drawLine(QPointF(x,top),QPointF(x,bottom))
        if self.hasFocus():
            p.setBrush(Qt.BrushStyle.NoBrush);p.setPen(QPen(QColor(accent),1))
            p.drawRect(self.rect().adjusted(1,1,-2,-2))
        p.setPen(QColor(muted))
        p.drawText(QRectF(left,self.height()-21,right-left,18),Qt.AlignmentFlag.AlignRight,"ترتیب رویدادها" if self.fa else "Event index · not physical time")
        p.end()


class SequentialView(QWidget):
    def __init__(self, theme, fa=False):
        super().__init__()
        self.fa=fa
        layout=QVBoxLayout(self)
        row=QHBoxLayout()
        self.selector=QComboBox()
        for key in MODELS:
            self.selector.addItem(TITLES[key][fa],key)
        row.addWidget(self.selector,1)
        self.clock=QPushButton("CLK = 0")
        self.clock.setCheckable(True)
        self.clock.toggled.connect(self.change_clock)
        row.addWidget(self.clock)
        pulse=QPushButton(self.t("Pulse clock","یک پالس ساعت"))
        pulse.setObjectName("primary")
        pulse.clicked.connect(self.pulse)
        row.addWidget(pulse)
        reset=QPushButton(self.t("Reset","بازنشانی"))
        reset.clicked.connect(self.reset)
        row.addWidget(reset)
        layout.addLayout(row)
        self.note=QLabel(self.t("Outputs update only on a rising clock edge. Waveforms show event order, not physical delay.",
              "خروجی‌ها فقط در لبه بالارونده ساعت تغییر می‌کنند. نمودار ترتیب رویدادهاست، نه تأخیر فیزیکی."))
        self.note.setWordWrap(True)
        layout.addWidget(self.note)
        self.input_layout=QGridLayout()
        layout.addLayout(self.input_layout)
        self.diagram=ClockedDiagram(theme)
        self.diagram.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        layout.addWidget(self.diagram,1)
        self.summary=QLabel()
        self.summary.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        layout.addWidget(self.summary)
        self.waveform=WaveformView(theme,self.fa)
        self.waveform.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        controls=QHBoxLayout()
        self.zoom=QComboBox()
        for length in (8,16,32,64):self.zoom.addItem(str(length),length)
        self.zoom.setCurrentIndex(1)
        controls.addWidget(QLabel(self.t("Visible samples","نمونه‌های قابل مشاهده")));controls.addWidget(self.zoom)
        self.follow=QCheckBox(self.t("Follow latest","دنبال‌کردن آخرین نمونه"));self.follow.setChecked(True);controls.addWidget(self.follow)
        self.position=QSlider(Qt.Orientation.Horizontal);self.position.setAccessibleName(self.t("History position","موقعیت تاریخچه"));controls.addWidget(self.position,1)
        export=QPushButton(self.t("Export CSV","خروجی CSV"));export.clicked.connect(self.export_history);controls.addWidget(export)
        self.details=MotionTabs()
        waveform_page=QWidget()
        waveform_layout=QVBoxLayout(waveform_page)
        waveform_layout.setContentsMargins(0,0,0,0)
        waveform_layout.addLayout(controls)
        waveform_layout.addWidget(self.waveform,3)
        self.inspection=QLabel();self.inspection.setWordWrap(True);self.inspection.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        waveform_layout.addWidget(self.inspection)
        self.details.addTab(waveform_page,self.t("Waveform","نمودار زمانی"))
        self.reference=FlipFlopReferenceView(self.fa)
        self.details.addTab(self.reference,self.t("Flip-flop tables","جدول‌های فلیپ‌فلاپ"))
        self.timing=TimingView(theme,self.fa)
        self.details.addTab(self.timing,self.t("Setup / hold","آماده‌سازی و نگهداری"))
        layout.addWidget(self.details,3)
        self.zoom.currentIndexChanged.connect(self.update_waveform)
        self.follow.toggled.connect(self.update_waveform)
        self.position.valueChanged.connect(self.seek)
        self.waveform.selected.connect(self.inspect)
        self.rule=QLabel()
        self.rule.setWordWrap(True)
        self.rule.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        layout.addWidget(self.rule)
        self.status=QLabel()
        self.status.setWordWrap(True)
        layout.addWidget(self.status)
        self.selector.currentIndexChanged.connect(self.load)
        self.load()

    def t(self,en,fa):
        return fa if self.fa else en

    def load(self):
        self.model=ClockedCircuit(self.selector.currentData())
        self.reference.set_kind(self.model.kind)
        while self.input_layout.count():
            item=self.input_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.buttons={}
        for i,name in enumerate(self.model.pins):
            button=QPushButton()
            button.setCheckable(True)
            button.toggled.connect(lambda v,n=name:self.input_changed(n,v))
            self.buttons[name]=button
            self.input_layout.addWidget(button,i//6,i%6)
        self.diagram.model=self.waveform.model=self.model
        self.cursor=None
        with QSignalBlocker(self.follow):self.follow.setChecked(True)
        formula,en,fa=RULES[self.model.kind]
        self.note.setText(self.t(en,fa)+"\n"+self.t("Rising-edge model; event order, not physical delay.","مدل لبه بالارونده؛ ترتیب رویدادها، نه تأخیر فیزیکی."))
        self.diagram.setMinimumHeight(max(155,60+18*(len(self.model.pins)+1)))
        self.waveform.setMinimumHeight(max(245,45+18*(1+len(self.model.pins)+len(self.model.outputs))))
        self.status.clear()
        self.refresh()

    def reset(self):
        self.model.reset()
        self.cursor=None
        with QSignalBlocker(self.follow):self.follow.setChecked(True)
        self.status.clear()
        self.refresh()

    def input_changed(self,name,value):
        self.model.set_input(name,int(value))
        self.status.clear()
        self.refresh()

    def change_clock(self,value):
        self.perform(lambda:self.model.set_clock(int(value)))

    def pulse(self):
        self.perform(self.model.pulse)

    def perform(self,fn):
        try:
            fn()
            self.status.clear()
        except ValueError:
            self.status.setText(self.t("SR = 11 is forbidden; edge rejected.","حالت SR = 11 نامعتبر است؛ لبه ساعت اعمال نشد."))
        self.refresh()

    def refresh(self):
        for name,button in self.buttons.items():
            button.blockSignals(True)
            button.setChecked(bool(self.model.inputs[name]))
            button.setText(f"{name} = {self.model.inputs[name]}")
            button.blockSignals(False)
        self.clock.blockSignals(True)
        self.clock.setChecked(bool(self.model.clock))
        self.clock.setText(f"CLK = {self.model.clock}")
        self.clock.blockSignals(False)
        self.summary.setText("   |   ".join(f"{n} = {v}" for n,v in self.model.outputs.items())+
                             (f"    HEX = {self.model.value:X}" if self.model.width>1 else ""))
        formula=RULES[self.model.kind][0]
        try:
            next_value=f"{self.model.next_value():0{self.model.width}b}"
        except ValueError:
            next_value=self.t("Invalid","نامعتبر")
        self.rule.setText(formula+"\n"+self.t("Next rising edge: ","لبه بالارونده بعدی: ")+next_value)
        self.diagram.update()
        self.update_waveform()

    def seek(self,*_):
        with QSignalBlocker(self.follow):self.follow.setChecked(False)
        self.update_waveform()

    def update_waveform(self,*_):
        names,rows=recorded(self.model)
        length=self.zoom.currentData()
        lo=rows[0].number;hi=rows[-min(length,len(rows))].number
        with QSignalBlocker(self.position):
            self.position.setRange(lo,hi)
            self.position.setValue(hi if self.follow.isChecked() else max(lo,min(hi,self.position.value())))
        visible=window(rows,length,self.position.value())
        if self.follow.isChecked():self.cursor=visible[-1].number
        elif not any(row.number==self.cursor for row in visible):self.cursor=visible[0].number
        self.waveform.set_window(names,visible,self.cursor)
        self.describe(names,visible)

    def inspect(self,number):
        with QSignalBlocker(self.follow):self.follow.setChecked(False)
        self.cursor=number
        self.describe(self.waveform.names,self.waveform.rows)

    def describe(self,names,rows):
        sample=next((row for row in rows if row.number==self.cursor),None)
        if sample:
            edge="  |  "+self.t("Rising edge","لبه بالارونده") if sample.rising else ""
            self.inspection.setText(f"#{sample.number}"+edge+"  |  "+"  ·  ".join(f"{n}={v}" for n,v in zip(names,sample.values)))
        else:self.inspection.clear()

    def export_history(self):
        path,_=QFileDialog.getSaveFileName(self,self.t("Export retained event samples","ذخیره نمونه‌های رویداد"),"waveform.csv","CSV (*.csv)")
        if path:
            try:self.write_history(path)
            except OSError:self.status.setText(self.t("Could not write file.","ذخیره فایل ممکن نبود."))

    def write_history(self,path):
        write_csv(self.model,path)
