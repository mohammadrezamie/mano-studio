"""Live schematic, binary input controls and truth tables from one netlist."""
from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QColor, QPen, QBrush, QFont, QPainter, QPainterPath
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton,
    QComboBox, QWidget, QGraphicsScene, QGraphicsView, QTableWidget,
    QTableWidgetItem, QHeaderView, QAbstractItemView, QSplitter,
)
from logic_engine import CIRCUITS
from ui.theme import PALETTES


class LogicDiagram(QGraphicsView):
    """Auto layout by signal depth. Rectangular labeled gates (IEC-inspired)."""
    def __init__(self, theme):
        super().__init__()
        self.theme = theme
        self.graph = QGraphicsScene(self)
        self.setScene(self.graph)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.setMinimumHeight(280)

    def draw(self, circuit, values):
        scene = self.graph
        scene.clear()
        bg,panel,raised,fg,muted,accent,border = PALETTES[self.theme]
        scene.setBackgroundBrush(QBrush(QColor(bg)))
        depth = {signal:0 for signal in circuit.inputs}
        columns = {0:list(circuit.inputs)}
        for gate in circuit.gates:
            d = 1 + max(depth[i] for i in gate.inputs)
            depth[gate.output] = d
            columns.setdefault(d,[]).append(gate.output)
        last = max(depth.values())+1
        columns[last] = [f"@{name}" for name,_ in circuit.outputs]
        positions = {}
        height = max(map(len,columns.values()))*76+36
        for col,names in columns.items():
            for index,name in enumerate(names):
                positions[name] = (28+col*180, (height-len(names)*76)/2+index*76)
        def wire(src,dst,index=0,count=1):
            x,y = positions[src]
            xx,yy = positions[dst]
            start_x,start_y = x+108,y+25
            end_y = yy+25+(index-(count-1)/2)*16
            middle = start_x+(xx-start_x)*0.55
            path=QPainterPath()
            path.moveTo(start_x,start_y)
            path.lineTo(middle,start_y)
            path.lineTo(middle,end_y)
            path.lineTo(xx,end_y)
            item=scene.addPath(path,QPen(QColor(accent if values[src] else muted),2 if values[src] else 1))
            item.setZValue(-1)
        for gate in circuit.gates:
            for i,src in enumerate(gate.inputs):
                wire(src,gate.output,i,len(gate.inputs))
        for name,signal in circuit.outputs:
            wire(signal,"@"+name)
        gate_names={gate.output:gate.op for gate in circuit.gates}
        output_signals=dict(circuit.outputs)
        def text_at(text,x,y,color,size=11):
            item=scene.addSimpleText(text,QFont("Segoe UI",size))
            item.setBrush(QBrush(QColor(color)))
            item.setPos(x,y)
        for name,(x,y) in positions.items():
            output=name.startswith("@")
            signal=output_signals[name[1:]] if output else name
            value=values[signal]
            title=name[1:] if output else gate_names.get(name,name)
            path=QPainterPath()
            path.addRoundedRect(QRectF(x,y,108,50),9,9)
            scene.addPath(path,QPen(QColor(accent if value else border),1.5),QBrush(QColor(panel)))
            text_at(title,x+9,y+5,fg)
            text_at(str(value),x+83,y+17,accent if value else muted,13)
            if name in gate_names:
                text_at(name,x+9,y+26,muted,9)
        scene.setSceneRect(scene.itemsBoundingRect().adjusted(-16,-16,16,16))

    def fit(self):
        if not self.graph.itemsBoundingRect().isEmpty():
            self.fitInView(self.graph.sceneRect(),Qt.AspectRatioMode.KeepAspectRatio)


class LogicLab(QDialog):
    def __init__(self,parent):
        super().__init__(parent)
        self.fa=parent.language=="fa"
        self.setWindowTitle("Mano Studio — Logic Lab")
        self.resize(1100,740)
        layout=QVBoxLayout(self)
        title=QLabel(self.t("Logic Lab · Digital circuits","آزمایشگاه مدار منطقی"))
        title.setObjectName("brand")
        layout.addWidget(title)
        row=QHBoxLayout()
        self.selector=QComboBox()
        for key,circuit in CIRCUITS.items():
            self.selector.addItem(circuit.title[self.fa],key)
        row.addWidget(self.selector,1)
        for en,fa,fn in [("Fit","نمای کامل",lambda:self.diagram.fit()),
            ("Zoom +","بزرگ‌نمایی",lambda:self.diagram.scale(1.2,1.2)),
            ("Zoom −","کوچک‌نمایی",lambda:self.diagram.scale(1/1.2,1/1.2))]:
            button=QPushButton(self.t(en,fa))
            button.clicked.connect(fn)
            row.addWidget(button)
        layout.addLayout(row)
        self.description=QLabel()
        self.description.setWordWrap(True)
        layout.addWidget(self.description)
        self.input_widget=QWidget()
        self.input_grid=QGridLayout(self.input_widget)
        layout.addWidget(self.input_widget)
        self.summary=QLabel()
        self.summary.setWordWrap(True)
        self.summary.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        layout.addWidget(self.summary)
        split=QSplitter(Qt.Orientation.Vertical)
        self.diagram=LogicDiagram(parent.theme)
        split.addWidget(self.diagram)
        self.table=QTableWidget()
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.table.cellClicked.connect(self.choose_row)
        split.addWidget(self.table)
        split.setSizes([400,220])
        layout.addWidget(split,1)
        self.selector.currentIndexChanged.connect(self.load)
        self.load()

    def t(self,en,fa):
        return fa if self.fa else en

    def load(self):
        self.circuit=CIRCUITS[self.selector.currentData()]
        self.inputs={name:0 for name in self.circuit.inputs}
        self.description.setText(self.circuit.explanation[self.fa])
        while self.input_grid.count():
            item=self.input_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.buttons={}
        for i,name in enumerate(self.inputs):
            button=QPushButton()
            button.setCheckable(True)
            button.toggled.connect(lambda checked,n=name:self.change(n,checked))
            self.buttons[name]=button
            self.input_grid.addWidget(button,i//6,i%6)
        self.rows=list(self.circuit.truth_table())
        headers=list(self.circuit.inputs)+[name for name,_ in self.circuit.outputs]
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.setRowCount(len(self.rows))
        for i,(bits,outputs) in enumerate(self.rows):
            for j,value in enumerate(bits+outputs):
                item=QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(i,j,item)
        self.refresh()
        self.diagram.fit()

    def change(self,name,value):
        self.inputs[name]=int(value)
        self.refresh()

    def choose_row(self,row,column):
        for name,value in zip(self.circuit.inputs,self.rows[row][0]):
            button=self.buttons[name]
            button.blockSignals(True)
            button.setChecked(bool(value))
            button.blockSignals(False)
            self.inputs[name]=value
        self.refresh()

    def refresh(self):
        for name,button in self.buttons.items():
            button.setText(f"{name} = {self.inputs[name]}")
        values=self.circuit.evaluate(self.inputs)
        self.summary.setText("   |   ".join(f"{name} = {values[signal]}" for name,signal in self.circuit.outputs))
        self.diagram.draw(self.circuit,values)
        bits=tuple(self.inputs.values())
        row=next(i for i,(inputs,_) in enumerate(self.rows) if inputs==bits)
        self.table.selectRow(row)
