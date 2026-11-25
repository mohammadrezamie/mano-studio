"""Editable encoded-state table, excitation equations and clock-step trace."""
from PySide6.QtCore import Qt, QSignalBlocker
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView,
    QPlainTextEdit)
from state_synthesis import design_state_machine
from state_analysis import analyze_machine
from ui.state_graph import StateGraph
from ui.motion import MotionTabs


class StateSynthesisView(QWidget):
    def __init__(self, fa=False):
        super().__init__()
        self.fa=fa
        self.state=0
        self.trace=[]
        self.next_boxes=[]
        self.out_boxes=[]
        box=QVBoxLayout(self)
        title=QLabel(self.t("State machine design","طراحی ماشین حالت"))
        title.setObjectName("brand")
        box.addWidget(title)
        hint=QLabel(self.t("Edit the complete transition table. Each clock uses the minimized excitation equations. Changing the table resets the simulated state and trace.",
                           "جدول کامل انتقال حالت را ویرایش کنید. هر پالس ساعت از معادلات تحریک ساده‌شده استفاده می‌کند. تغییر جدول، حالت و تاریخچه شبیه‌سازی را بازنشانی می‌کند."))
        hint.setWordWrap(True)
        box.addWidget(hint)
        row=QHBoxLayout()
        row.addWidget(QLabel(self.t("State bits","بیت‌های حالت")))
        self.width=QComboBox()
        for n in (1,2,3):self.width.addItem(str(n),n)
        row.addWidget(self.width)
        row.addWidget(QLabel(self.t("Model","مدل")))
        self.mode=QComboBox()
        self.mode.addItem(self.t("Moore","مور"),"Moore")
        self.mode.addItem(self.t("Mealy","میلی"),"Mealy")
        row.addWidget(self.mode)
        row.addWidget(QLabel(self.t("Flip-flop","فلیپ‌فلاپ")))
        self.ff=QComboBox()
        for name in ("D","T","JK"):self.ff.addItem(name,name)
        row.addWidget(self.ff)
        example=QPushButton(self.t("Counter example","مثال شمارنده"))
        example.clicked.connect(self.rebuild)
        row.addWidget(example)
        box.addLayout(row)
        middle=QHBoxLayout()
        self.table=QTableWidget(0,4)
        self.table.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.table.setAccessibleName(self.t("Editable state transition table","جدول قابل ویرایش انتقال حالت"))
        self.table.setHorizontalHeaderLabels(["Q","X","Q⁺","Y"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().hide()
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        middle.addWidget(self.table,3)
        side=QVBoxLayout()
        self.equations=QPlainTextEdit()
        self.equations.setReadOnly(True)
        self.equations.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.views=MotionTabs()
        self.graph=StateGraph(self.fa)
        self.views.addTab(self.graph,self.t("Transitions","نمودار انتقال"))
        self.views.addTab(self.equations,self.t("Equations","معادلات"))
        self.analysis_text=QPlainTextEdit()
        self.analysis_text.setReadOnly(True)
        self.analysis_text.setAccessibleName(self.t("State reachability and equivalence","دسترس‌پذیری و هم‌ارزی حالت‌ها"))
        self.views.addTab(self.analysis_text,self.t("Analysis","تحلیل"))
        side.addWidget(self.views,1)
        self.graph_note=QLabel()
        self.graph_note.setWordWrap(True)
        side.addWidget(self.graph_note)
        self.mapping=QLabel()
        self.mapping.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.mapping.setWordWrap(True)
        side.addWidget(self.mapping)
        middle.addLayout(side,2)
        box.addLayout(middle,3)
        controls=QHBoxLayout()
        self.input=QComboBox()
        for n in (0,1):self.input.addItem(f"X = {n}",n)
        self.input.setAccessibleName(self.t("Binary input X","ورودی دودویی X"))
        controls.addWidget(self.input)
        self.clock=QPushButton(self.t("Clock step","پالس ساعت"))
        self.clock.setObjectName("primary")
        self.clock.clicked.connect(self.pulse)
        controls.addWidget(self.clock)
        reset=QPushButton(self.t("Reset Q","بازنشانی Q"))
        reset.clicked.connect(self.reset_state)
        controls.addWidget(reset)
        self.status=QLabel()
        self.status.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        controls.addWidget(self.status,1)
        box.addLayout(controls)
        box.addWidget(QLabel(self.t("Trace: Q, X → Q next, Y before edge","ردیابی: حالت، ورودی، حالت بعد و خروجی پیش از لبه")))
        self.history=QPlainTextEdit()
        self.history.setReadOnly(True)
        self.history.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        box.addWidget(self.history,1)
        self.width.currentIndexChanged.connect(self.rebuild)
        self.mode.currentIndexChanged.connect(self.change_mode)
        self.ff.currentIndexChanged.connect(self.refresh)
        self.input.currentIndexChanged.connect(self.preview)
        self.rebuild()

    def t(self,en,fa):
        return fa if self.fa else en

    def rebuild(self,*_):
        n=self.width.currentData()
        size=2**n
        self.table.setRowCount(0)
        self.table.setRowCount(size*2)
        self.next_boxes=[]
        self.out_boxes=[]
        for i in range(size*2):
            q,x=divmod(i,2)
            for col,value in enumerate((f"{q:0{n}b}",str(x))):
                item=QTableWidgetItem(value)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(i,col,item)
            nxt=QComboBox()
            for j in range(size):nxt.addItem(f"{j:0{n}b}",j)
            nxt.setCurrentIndex((q+x)%size)
            nxt.setAccessibleName(self.t(f"Next state, row {i}",f"حالت بعد، ردیف {i}"))
            self.table.setCellWidget(i,2,nxt)
            self.next_boxes.append(nxt)
            out=QComboBox()
            for y in (0,1):out.addItem(str(y),y)
            out.setCurrentIndex(q==size-1)
            out.setAccessibleName(self.t(f"Output, row {i}",f"خروجی، ردیف {i}"))
            self.table.setCellWidget(i,3,out)
            self.out_boxes.append(out)
        for i,(nxt,out) in enumerate(zip(self.next_boxes,self.out_boxes)):
            nxt.currentIndexChanged.connect(self.refresh)
            out.currentIndexChanged.connect(lambda _,row=i:self.output_changed(row))
        self.change_mode()

    def change_mode(self,*_):
        moore=self.mode.currentData()=="Moore"
        for i,out in enumerate(self.out_boxes):
            with QSignalBlocker(out):
                if moore and i%2:out.setCurrentIndex(self.out_boxes[i-1].currentIndex())
            out.setEnabled(not moore or i%2==0)
        self.refresh()

    def output_changed(self,i):
        if self.mode.currentData()=="Moore" and i%2==0:
            with QSignalBlocker(self.out_boxes[i+1]):
                self.out_boxes[i+1].setCurrentIndex(self.out_boxes[i].currentIndex())
        self.refresh()

    def refresh(self,*_):
        rows=tuple((n.currentData(),y.currentData()) for n,y in zip(self.next_boxes,self.out_boxes))
        self.model=design_state_machine(self.width.currentData(),rows,self.mode.currentData(),self.ff.currentData())
        self.equations.setPlainText("\n".join(f"{name} = {cover.expression}" for name,cover in self.model.equations))
        self.mapping.setText("  |  ".join(f"{a} = {q}" for a,q in self.model.aliases))
        self.refresh_analysis()
        self.reset_state()

    def refresh_analysis(self):
        self.analysis=analyze_machine(self.model)
        bits=self.model.bits
        label=lambda q:f"{q:0{bits}b}"
        empty=self.t("reset","بازنشانی")
        none=self.t("None","هیچ")
        lines=[self.t("Shortest input paths from reset Q=0","کوتاه‌ترین مسیرهای ورودی از بازنشانی Q=0")]
        lines.extend(f"{label(q)}: {word or empty}" for q,word in self.analysis.paths)
        lines.extend(["",self.t("Unreachable states","حالت‌های دسترس‌ناپذیر"),
                      ", ".join(map(label,self.analysis.unreachable)) or none,
                      "",self.t("Equivalent classes (all encoded states)","کلاس‌های هم‌ارزی (همه حالت‌های کدشده)")])
        lines.extend(" = ".join(map(label,group)) for group in self.analysis.classes)
        lines.extend(["",self.t("Shortest distinguishing input sequences","کوتاه‌ترین دنباله‌های ورودی متمایزکننده"),
                      self.t("Outputs sampled before each clock. Equivalent pairs have no distinguishing sequence.",
                             "خروجی پیش از هر پالس ساعت نمونه‌برداری می‌شود. حالت‌های هم‌ارز دنباله متمایزکننده ندارند.")])
        for a,b,word in self.analysis.witnesses:
            lines.append(f"{label(a)} / {label(b)}: "+(word if word is not None else self.t("equivalent","هم‌ارز")))
        self.analysis_text.setPlainText("\n".join(lines))

    def reset_state(self,*_):
        self.state=0
        self.trace=[]
        self.history.clear()
        self.preview()

    def preview(self,*_):
        n=self.model.bits
        nxt,y=self.model.step(self.state,self.input.currentData())
        self.status.setText(f"Q={self.state:0{n}b}   Q⁺={nxt:0{n}b}   Y={y}")
        self.graph.set_state(self.model,self.state,self.input.currentData())
        self.graph_note.setText(self.t("Current state's outgoing edges; ▶ marks the next edge, not a completed clock. Node: Q / Y; edge: X.",
                                      "مسیرهای خروجی حالت جاری؛ ▶ مسیر بعدی است، نه پالس اجراشده. گره: Q / Y؛ یال: X.")
                                if self.model.mode=="Moore" else
                                self.t("Current state's outgoing edges; ▶ marks the next edge. Node: Q; edge: X / Y before clock.",
                                       "مسیرهای خروجی حالت جاری؛ ▶ مسیر بعدی است. گره: Q؛ یال: X / Y پیش از ساعت."))

    def pulse(self,*_):
        n=self.model.bits
        x=self.input.currentData()
        nxt,y=self.model.step(self.state,x)
        self.trace.append(f"{self.state:0{n}b}, {x} → {nxt:0{n}b}, {y}")
        self.trace=self.trace[-64:]
        self.history.setPlainText("\n".join(self.trace))
        self.state=nxt
        self.preview()
