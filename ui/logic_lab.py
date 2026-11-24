"""Live schematic, binary input controls and truth tables from one netlist."""
from pathlib import Path
from PySide6.QtCore import Qt, QRectF, QPointF, Signal
from PySide6.QtGui import QColor, QPen, QBrush, QFont, QPainter, QPainterPath
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton,
    QComboBox, QWidget, QGraphicsScene, QGraphicsView, QTableWidget,
    QTableWidgetItem, QHeaderView, QAbstractItemView, QSplitter, QSpinBox, QStackedWidget, QFileDialog, QMessageBox,
)
from logic_engine import CIRCUITS, ARITY, basic
from circuit_document import CircuitDocument
from schematic_routing import wire_route
from ui.circuit_editor import CircuitEditor
from ui.gate_symbols import draw_gate, input_point, output_point, WIDTH, HEIGHT, CENTER
from ui.theme import PALETTES


class LogicDiagram(QGraphicsView):
    """Auto layout by signal depth, with distinctive-shape symbols and pins."""
    rewire = Signal(str, str, int)
    moved = Signal(str, float, float)
    hint = Signal(str)

    def __init__(self, theme):
        super().__init__()
        self.theme = theme
        self.graph = QGraphicsScene(self)
        self.setScene(self.graph)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.setMinimumHeight(280)
        self.editing=False
        self.positions={}
        self.ports=[]
        self.pending=None
        self.drag_node=None
        self.preview=None
        self.setMouseTracking(True)

    def draw(self, circuit, values, placement=()):
        scene = self.graph
        self.clear_gesture()
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
        positions.update({name:(x,y) for name,x,y in placement if name in positions})
        self.positions=positions
        self.ports=[]
        for name in circuit.inputs:
            self.ports.append((name,-1,output_point(*positions[name])))
        for gate in circuit.gates:
            self.ports.append((gate.output,-1,output_point(*positions[gate.output])))
            for i in range(len(gate.inputs)):
                self.ports.append((gate.output,i,input_point(*positions[gate.output],i,len(gate.inputs))))
        for name,_ in circuit.outputs:
            self.ports.append(("@"+name,0,input_point(*positions["@"+name],0,1)))
        fanout = {}
        for src,dst,i,count in edges:
            fanout.setdefault(src,[]).append((dst,i,count))
        lane_counts = {}
        long_index = 0
        for src,targets in fanout.items():
            sx,sy = output_point(*positions[src])
            pen = QPen(QColor(accent if values[src] else muted),2 if values[src] else 1.1)
            trunk = sx + 8
            if not placement:
                scene.addLine(sx,sy,trunk,sy,pen).setZValue(-1)
            for dst,index,count in targets:
                ex,ey = input_point(*positions[dst],index,count)
                if placement:
                    obstacles=[(x,y,x+WIDTH,y+HEIGHT) for name,(x,y) in positions.items() if name not in (src,dst)]
                    # Protect source/target bodies too: pins sit at the edges.
                    obstacles += [(positions[n][0],positions[n][1],positions[n][0]+WIDTH,positions[n][1]+HEIGHT) for n in (src,dst)]
                    route,clear=wire_route((sx,sy),(ex,ey),obstacles,long_index)
                    long_index+=1
                    path=QPainterPath(QPointF(*route[0]))
                    for point in route[1:]:
                        path.lineTo(*point)
                    route_pen=QPen(pen)
                    if not clear:
                        route_pen.setStyle(Qt.PenStyle.DashLine)
                    scene.addPath(path,route_pen).setZValue(-1)
                    continue
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
            if len(targets)>1 and not placement:
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
        if self.editing:
            for name,pin,(x,y) in self.ports:
                dot=scene.addEllipse(QRectF(x-5,y-5,10,10),QPen(QColor(accent),1.5),QBrush(QColor(panel)))
                dot.setZValue(3)
                dot.setToolTip(f"{name}: " + ("source" if pin<0 else f"pin {pin+1}"))
        scene.setSceneRect(scene.itemsBoundingRect().adjusted(-40,-40,40,40))

    def clear_gesture(self):
        if self.preview is not None:
            self.graph.removeItem(self.preview)
            self.preview=None
        self.pending=None
        self.drag_node=None

    def set_editing(self, enabled):
        self.clear_gesture()
        self.editing=enabled
        self.setDragMode(QGraphicsView.DragMode.NoDrag if enabled else QGraphicsView.DragMode.ScrollHandDrag)

    def port_at(self, point, receiving=None):
        best=None
        distance=12**2
        for name,pin,(x,y) in self.ports:
            if receiving is not None and (pin>=0)!=receiving:
                continue
            screen=self.mapFromScene(QPointF(x,y))
            delta=(screen.x()-point.x())**2+(screen.y()-point.y())**2
            if delta<=distance:
                best=(name,pin,(x,y))
                distance=delta
        return best

    def mousePressEvent(self,event):
        if not self.editing or event.button()!=Qt.MouseButton.LeftButton:
            return super().mousePressEvent(event)
        point=event.position().toPoint()
        target=self.port_at(point,True) if self.pending else None
        if target:
            source=self.pending[0]
            self.clear_gesture()
            self.rewire.emit(source,target[0],target[1])
            return
        source=self.port_at(point,False)
        if source:
            self.clear_gesture()
            self.pending=source
            x,y=source[2]
            self.preview=self.graph.addLine(x,y,x,y,QPen(QColor(PALETTES[self.theme][5]),2,Qt.PenStyle.DashLine))
            self.preview.setZValue(4)
            self.hint.emit("source")
            return
        self.clear_gesture()
        p=self.mapToScene(point)
        for name,(x,y) in reversed(list(self.positions.items())):
            if QRectF(x+9,y,WIDTH-18,HEIGHT).contains(p):
                self.drag_node=(name,p.x()-x,p.y()-y)
                self.preview=self.graph.addRect(QRectF(x,y,WIDTH,HEIGHT),QPen(QColor(PALETTES[self.theme][5]),1.5,Qt.PenStyle.DashLine))
                self.preview.setZValue(4)
                return

    def mouseMoveEvent(self,event):
        if not self.editing or self.preview is None:
            return super().mouseMoveEvent(event)
        p=self.mapToScene(event.position().toPoint())
        if self.pending:
            x,y=self.pending[2]
            self.preview.setLine(x,y,p.x(),p.y())
        elif self.drag_node:
            _,dx,dy=self.drag_node
            self.preview.setRect(QRectF(p.x()-dx,p.y()-dy,WIDTH,HEIGHT))

    def mouseReleaseEvent(self,event):
        if self.editing and self.drag_node and event.button()==Qt.MouseButton.LeftButton:
            name,dx,dy=self.drag_node
            p=self.mapToScene(event.position().toPoint())
            x,y=round((p.x()-dx)/10)*10,round((p.y()-dy)/10)*10
            self.clear_gesture()
            if abs(x-self.positions[name][0])+abs(y-self.positions[name][1])<6:
                return
            if any(QRectF(x,y,WIDTH,HEIGHT).adjusted(-6,-6,6,6).intersects(QRectF(xx,yy,WIDTH,HEIGHT))
                   for other,(xx,yy) in self.positions.items() if other!=name):
                self.hint.emit("overlap")
                return
            self.moved.emit(name,float(x),float(y))
            return
        if not self.editing:
            super().mouseReleaseEvent(event)

    def keyPressEvent(self,event):
        if self.editing and event.key()==Qt.Key.Key_Escape and (self.pending or self.drag_node):
            self.clear_gesture()
            self.hint.emit("ready")
            return
        super().keyPressEvent(event)

    def fit(self):
        if not self.graph.itemsBoundingRect().isEmpty():
            self.fitInView(self.graph.sceneRect(),Qt.AspectRatioMode.KeepAspectRatio)


class LogicLab(QDialog):
    def __init__(self,parent):
        super().__init__(parent)
        self.fa=parent.language=="fa"
        self.history=[]
        self.dirty=False
        self.document=None
        self.selected_key=None
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
        self.selector.addItem(self.t("Custom circuit","مدار دلخواه"),"custom")
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
        actions=QHBoxLayout()
        self.document_buttons=[]
        for en,fa,fn in [("Edit circuit","ویرایش مدار",self.edit_circuit),("Open circuit","باز کردن مدار",self.open_circuit),("Save circuit","ذخیره مدار",self.save_circuit),("Undo edit","واگرد ویرایش",self.undo_edit)]:
            button=QPushButton(self.t(en,fa))
            button.clicked.connect(fn)
            actions.addWidget(button)
            self.document_buttons.append(button)
            if en=="Undo edit":
                self.undo_button=button
        actions.addStretch()
        layout.addLayout(actions)
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
        self.stack=QStackedWidget()
        self.stack.addWidget(split)
        self.circuit_editor=CircuitEditor(self.fa)
        self.stack.addWidget(self.circuit_editor)
        self.circuit_editor.applied.connect(self.apply_document)
        self.circuit_editor.cancelled.connect(self.cancel_edit)
        layout.addWidget(self.stack,1)
        self.selector.currentIndexChanged.connect(self.load)
        self.pin_count.valueChanged.connect(self.load)
        self.load()

    def t(self,en,fa):
        return fa if self.fa else en

    def load(self):
        key=self.selector.currentData()
        if key!=self.selected_key and self.dirty and not self.confirm_discard():
            self.selector.blockSignals(True)
            self.selector.setCurrentIndex(self.selector.findData(self.selected_key))
            self.selector.blockSignals(False)
            return
        variable=key.upper() in ARITY and key!="not"
        self.pin_count.setEnabled(variable)
        self.selected_key=key
        if key=="custom":
            self.circuit=basic("AND")
        else:
            self.circuit=basic(key.upper(),self.pin_count.value()) if variable else CIRCUITS[key]
        self.document=CircuitDocument.from_circuit(self.circuit)
        self.history.clear()
        self.dirty=False
        self.show_circuit()

    def show_circuit(self):
        self.cancel_edit()
        self.undo_button.setEnabled(bool(self.history))
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

    def confirm_discard(self):
        if not self.dirty:
            return True
        return QMessageBox.question(self,self.t("Unsaved circuit","مدار ذخیره‌نشده"),
            self.t("Discard unsaved circuit changes?","تغییرات ذخیره‌نشده مدار حذف شوند؟"),
            QMessageBox.StandardButton.Discard|QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Cancel)==QMessageBox.StandardButton.Discard

    def edit_circuit(self):
        self.circuit_editor.load(self.document)
        self.stack.setCurrentIndex(1)
        self.selector.setEnabled(False)
        self.pin_count.setEnabled(False)
        self.input_widget.setEnabled(False)
        for button in self.document_buttons:
            button.setEnabled(False)

    def cancel_edit(self):
        self.stack.setCurrentIndex(0)
        self.selector.setEnabled(True)
        key=self.selector.currentData()
        self.pin_count.setEnabled(key.upper() in ARITY and key!="not")
        self.input_widget.setEnabled(True)
        for button in self.document_buttons:
            button.setEnabled(True)
        self.undo_button.setEnabled(bool(self.history))

    def install_document(self,document,dirty):
        circuit=document.compile()
        self.document,self.circuit=document,circuit
        self.dirty=dirty
        self.selected_key="custom"
        self.selector.blockSignals(True)
        self.selector.setCurrentIndex(self.selector.findData("custom"))
        self.selector.blockSignals(False)
        self.pin_count.setEnabled(False)
        self.show_circuit()

    def apply_document(self,document):
        if document!=self.document:
            self.history.append((self.document,self.dirty))
            self.history=self.history[-30:]
            self.install_document(document,True)
        else:
            self.cancel_edit()

    def undo_edit(self):
        if self.history:
            document,dirty=self.history.pop()
            self.install_document(document,dirty)

    def open_circuit(self):
        if not self.confirm_discard():
            return
        name,_=QFileDialog.getOpenFileName(self,self.t("Open circuit","باز کردن مدار"),"","Mano circuit (*.mano-logic.json);;JSON (*.json)")
        if not name:
            return
        try:
            path=Path(name)
            if path.stat().st_size>200000:
                raise ValueError("Circuit file too large.")
            document=CircuitDocument.loads(path.read_text(encoding="utf-8"))
        except (OSError,UnicodeError,ValueError) as exc:
            QMessageBox.warning(self,self.t("Invalid circuit","مدار نامعتبر"),str(exc))
            return
        self.history.clear()
        self.install_document(document,False)

    def save_circuit(self):
        if self.stack.currentIndex()==1:
            QMessageBox.information(self,self.t("Apply first","ابتدا اعمال کنید"),
                self.t("Apply or cancel the staged edit before saving.","پیش از ذخیره، ویرایش را اعمال یا لغو کنید."))
            return
        name,_=QFileDialog.getSaveFileName(self,self.t("Save circuit","ذخیره مدار"),"circuit.mano-logic.json","Mano circuit (*.mano-logic.json);;JSON (*.json)")
        if not name:
            return
        path=Path(name)
        if not path.suffix:
            path=path.with_suffix(".mano-logic.json")
        try:
            path.write_text(self.document.dumps(),encoding="utf-8")
        except (OSError,ValueError) as exc:
            QMessageBox.warning(self,self.t("Cannot save","ذخیره ناموفق"),str(exc))
            return
        self.dirty=False
        # Undo after saving changes the document relative to the saved file.
        self.history=[(document,True) for document,_ in self.history]

    def done(self,result):
        if self.stack.currentIndex()==1 and QMessageBox.question(self,self.t("Unapplied edits","ویرایش اعمال‌نشده"),self.t("Discard staged edits?","ویرایش‌های اعمال‌نشده حذف شوند؟"),QMessageBox.StandardButton.Discard|QMessageBox.StandardButton.Cancel,QMessageBox.StandardButton.Cancel)!=QMessageBox.StandardButton.Discard:
            return
        if self.confirm_discard():
            super().done(result)

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
