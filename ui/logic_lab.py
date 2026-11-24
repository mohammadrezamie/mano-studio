"""Live schematic, binary input controls and truth tables from one netlist."""
from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QColor, QPen, QBrush, QFont, QPainter, QPainterPath
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton,
    QComboBox, QWidget, QGraphicsScene, QGraphicsView, QTableWidget,
    QTableWidgetItem, QHeaderView, QAbstractItemView, QSplitter, QSpinBox,
)
from logic_engine import CIRCUITS, ARITY, basic
from ui.gate_symbols import draw_gate, input_point, output_point, WIDTH, HEIGHT, CENTER
from ui.theme import PALETTES


class LogicDiagram(QGraphicsView):
    """Auto layout by signal depth, with distinctive-shape symbols and pins."""
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
        # Separate long routes above the symbols so they cannot run through gates.
        depths = dict(depth)
        depths.update({"@"+name:last for name,_ in circuit.outputs})
        edges = [(src,gate.output,i,len(gate.inputs))
                 for gate in circuit.gates for i,src in enumerate(gate.inputs)]
        edges += [(src,"@"+name,0,1) for name,src in circuit.outputs]
        long_edges = [edge for edge in edges if depths[edge[1]]-depths[edge[0]]>1]
        top = 28 + len(long_edges)*9
        pitch = 126
        height = max(map(len,columns.values()))*pitch+36
        for col,names in columns.items():
            for index,name in enumerate(names):
                positions[name] = (28+col*220, top+(height-len(names)*pitch)/2+index*pitch)
        fanout = {}
        for src,dst,i,count in edges:
            fanout.setdefault(src,[]).append((dst,i,count))
        lane_counts = {}
        long_index = 0
        for src,targets in fanout.items():
            sx,sy = output_point(*positions[src])
            pen = QPen(QColor(accent if values[src] else muted),2 if values[src] else 1.1)
            trunk = sx + 8
            scene.addLine(sx,sy,trunk,sy,pen).setZValue(-1)
            for dst,index,count in targets:
                ex,ey = input_point(*positions[dst],index,count)
                gap = depths[dst]-1
                lane = lane_counts.get(gap,0)
                lane_counts[gap] = lane+1
                # Adjacent gap is wide enough for a range of separate tracks.
                middle = ex-12-(lane%12)*7
                path = QPainterPath()
                path.moveTo(trunk,sy)
                if depths[dst]-depths[src]>1:
                    route_y = 14+long_index*9
                    long_index += 1
                    path.lineTo(trunk,route_y)
                    path.lineTo(middle,route_y)
                    path.lineTo(middle,ey)
                else:
                    path.lineTo(middle,sy)
                    path.lineTo(middle,ey)
                path.lineTo(ex,ey)
                scene.addPath(path,pen).setZValue(-1)
            if len(targets)>1:
                scene.addEllipse(QRectF(trunk-3,sy-3,6,6),pen,QBrush(pen.color()))
        gate_names={gate.output:gate for gate in circuit.gates}
        output_signals=dict(circuit.outputs)
        def text_at(text,x,y,color,size=11):
            item=scene.addSimpleText(text,QFont("Segoe UI",size))
            item.setBrush(QBrush(QColor(color)))
            item.setPos(x,y)
            return item
        for name,(x,y) in positions.items():
            output=name.startswith("@")
            signal=output_signals[name[1:]] if output else name
            value=values[signal]
            if name in gate_names:
                gate=gate_names[name]
                draw_gate(scene,gate.op,x,y,tuple(values[i] for i in gate.inputs),value,PALETTES[self.theme])
                text_at(gate.op,x+25,y+HEIGHT+3,fg,10)
                text_at(name,x+25,y-17,muted,9)
            else:
                title=name[1:] if output else name
                color=accent if value else muted
                pin_x=x if output else x+WIDTH
                scene.addLine(pin_x,y+CENTER,x+(22 if output else 86),y+CENTER,QPen(QColor(color),1.8))
                body=QPainterPath()
                body.addRoundedRect(QRectF(x+22,y+CENTER-21,64,42),6,6)
                scene.addPath(body,QPen(QColor(color),1.5),QBrush(QColor(panel)))
                text_at(title,x+25,y+CENTER-19,fg,10)
                text_at(str(value),x+69,y+CENTER, color,12)
                scene.addEllipse(QRectF(pin_x-2,y+CENTER-2,4,4),QPen(QColor(color)),QBrush(QColor(color)))
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
        row.addWidget(QLabel(self.t("Gate inputs","تعداد ورودی گیت")))
        self.pin_count=QSpinBox()
        self.pin_count.setRange(2,4)
        self.pin_count.setValue(2)
        row.addWidget(self.pin_count)
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
        self.pin_count.valueChanged.connect(self.load)
        self.load()

    def t(self,en,fa):
        return fa if self.fa else en

    def load(self):
        key=self.selector.currentData()
        variable=key.upper() in ARITY and key!="not"
        self.pin_count.setEnabled(variable)
        self.circuit=basic(key.upper(),self.pin_count.value()) if variable else CIRCUITS[key]
        self.inputs={name:0 for name in self.circuit.inputs}
        self.description.setText(self.circuit.explanation[self.fa]+"  |  "+self.t("Inputs / Outputs", "ورودی / خروجی")+f": {len(self.circuit.inputs)} / {len(self.circuit.outputs)}")
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
