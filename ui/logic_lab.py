"""Live schematic, binary input controls and truth tables from one netlist."""
from pathlib import Path
from ui.motion import MotionTabs, motion_allowed
from ui.signal_motion import changed_routes
from ui.navigation_rail import NavigationRail
import csv
from PySide6.QtCore import Qt, QRectF, QPointF, Signal, QSize, QVariantAnimation, QEasingCurve
from PySide6.QtGui import QColor, QPen, QBrush, QFont, QPainter, QPainterPath
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton,
    QComboBox, QWidget, QGraphicsScene, QGraphicsView, QTableWidget,
    QTableWidgetItem, QHeaderView, QAbstractItemView, QSplitter, QSpinBox, QStackedWidget, QFileDialog, QMessageBox, QMenu, QTabWidget, QPlainTextEdit,
)
from PySide6.QtSvg import QSvgGenerator
from logic_engine import CIRCUITS, ARITY, basic, circuit_equations
from circuit_document import CircuitDocument
from schematic_routing import wire_route
from wire_notation import analyze_wires
from ui.circuit_editor import CircuitEditor
from ui.localization import error_text
from ui.sequential_view import SequentialView
from ui.memory_view import MemoryView
from ui.memory_array_view import MemoryArrayView
from ui.bus_view import BusView
from ui.databus_view import DatabusView
from ui.cache_view import CacheView
from ui.karnaugh_view import KarnaughView
from ui.state_synthesis_view import StateSynthesisView
from boolean_synthesis import synthesize
from universal_gates import universalize
from mux_synthesis import synthesize_mux
from classic_samples import SAMPLES, load_sample
from native_circuit import load_circuit, save_circuit
from ui.block_dialog import BlockDialog
from ui.virtual_memory_view import AddressTranslationView
from ui.gate_symbols import draw_gate, input_point, output_point, WIDTH, HEIGHT, CENTER
from ui.theme import PALETTES, STATUS


class LogicDiagram(QGraphicsView):
    """Auto layout by signal depth, with distinctive-shape symbols and pins."""
    rewire = Signal(str, str, int)
    moved = Signal(str, float, float)
    hint = Signal(str)

    def __init__(self, theme, fa=False, symbol_style="ansi", *, reduced_motion=False):
        super().__init__()
        self.theme = theme
        self.fa = fa
        self.reduced_motion = bool(reduced_motion)
        self.symbol_style=symbol_style if symbol_style in ("ansi","iec") else "ansi"
        self.graph = QGraphicsScene(self)
        self.setScene(self.graph)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.setMinimumHeight(280)
        self.setAccessibleName("شماتیک مدار منطقی" if fa else "Logic circuit schematic")
        self.setAccessibleDescription("پایه‌ها، مقدار بیت و مسیرهای اتصال؛ حلقه هشدار به معنای اتصال نیست. درخشش، تغییر مقدار را نشان می‌دهد، نه تأخیر انتشار." if fa else "Functional pins, bit values and net routes; warning rings are not connections. Glow indicates value changes, not propagation delay.")
        self.editing=False
        self.positions={}
        self.route_cache={}
        self.route_key=None
        self.unrouted=0
        self.notation_key=None
        self.notation=((),())
        self.ambiguous=0
        self.ports=[]
        self.pending=None
        self.drag_node=None
        self.preview=None
        self.setMouseTracking(True)
        self.setProperty("manoMotionSurface", True)
        self._last_circuit = None
        self._last_values = None
        self._last_route_key = None
        self._changed_paths = ()
        self._pulse = 0.0
        self._net_animation = QVariantAnimation(self)
        self._net_animation.setDuration(320)
        self._net_animation.setStartValue(1.0)
        self._net_animation.setEndValue(0.0)
        self._net_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._net_animation.valueChanged.connect(self._pulse_frame)
        self._net_animation.finished.connect(self.snap)

    def _pulse_frame(self, value):
        self._pulse = float(value)
        self.viewport().update()

    def snap(self):
        self._net_animation.stop()
        self._changed_paths = ()
        self._pulse = 0.0
        self.viewport().update()

    def hideEvent(self, event):
        self.snap()
        super().hideEvent(event)

    def drawForeground(self, painter, rect):
        super().drawForeground(painter, rect)
        if not self._changed_paths or self._pulse <= 0:
            return
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        color = QColor(PALETTES[self.theme][5])
        color.setAlpha(round(76 * self._pulse))
        painter.setPen(QPen(color, 6, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        for _, points in self._changed_paths:
            path = QPainterPath(QPointF(*points[0]))
            for point in points[1:]:
                path.lineTo(*point)
            painter.drawPath(path)
        painter.restore()

    def draw(self, circuit, values, placement=()):
        self.snap()
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
        fixed={name:(x,y) for name,x,y in placement if name in positions}
        positions.update(fixed)
        # Keep new components from covering saved positions after a table edit.
        occupied=list(fixed.values())
        for name,(x,y) in positions.items():
            if name in fixed:
                continue
            while any(abs(x-xx)<WIDTH+6 and abs(y-yy)<HEIGHT+6 for xx,yy in occupied):
                y+=pitch
            positions[name]=(x,y)
            occupied.append((x,y))
        route_key=(tuple(positions.items()),tuple(edges))
        if route_key!=self.route_key:
            self.route_cache.clear()
            self.route_key=route_key
        self.unrouted=0
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
        routes=[]
        for src,targets in fanout.items():
            sx,sy = output_point(*positions[src])
            pen = QPen(QColor(accent if values[src] else muted),2 if values[src] else 1.1)
            trunk = sx + 8
            if not placement:
                scene.addLine(sx,sy,trunk,sy,pen).setZValue(-1)
                routes.append((src,((sx,sy),(trunk,sy))))
            for dst,index,count in targets:
                ex,ey = input_point(*positions[dst],index,count)
                if placement:
                    obstacles=[(x,y,x+WIDTH,y+HEIGHT) for name,(x,y) in positions.items() if name not in (src,dst)]
                    # Protect source/target bodies too: pins sit at the edges.
                    obstacles += [(positions[n][0],positions[n][1],positions[n][0]+WIDTH,positions[n][1]+HEIGHT) for n in (src,dst)]
                    key=(src,dst,index)
                    if key not in self.route_cache:
                        self.route_cache[key]=wire_route((sx,sy),(ex,ey),obstacles,long_index)
                    route,clear=self.route_cache[key]
                    routes.append((src,tuple(route)))
                    long_index+=1
                    path=QPainterPath(QPointF(*route[0]))
                    for point in route[1:]:
                        path.lineTo(*point)
                    route_pen=QPen(pen)
                    if not clear:
                        self.unrouted+=1
                        route_pen.setStyle(Qt.PenStyle.DashLine)
                    scene.addPath(path,route_pen).setZValue(-1)
                    continue
                gap = depths[dst]-1
                lane = lane_counts.get(gap,0)
                lane_counts[gap] = lane+1
                # Adjacent gap is wide enough for a range of separate tracks.
                middle = ex-12-(lane%12)*7
                points=[(trunk,sy)]
                if depths[dst]-depths[src]>1:
                    route_y = 14+long_index*9
                    long_index += 1
                    points.extend(((trunk,route_y),(middle,route_y),(middle,ey)))
                else:
                    points.extend(((middle,sy),(middle,ey)))
                points.append((ex,ey))
                routes.append((src,tuple(points)))
                path=QPainterPath(QPointF(*points[0]))
                for point in points[1:]:path.lineTo(*point)
                scene.addPath(path,pen).setZValue(-1)
        notation_key=tuple(routes)
        if notation_key!=self.notation_key:
            self.notation=analyze_wires(routes)
            self.notation_key=notation_key
        junctions,conflicts=self.notation
        self.ambiguous=len(conflicts)
        for net,x,y in junctions:
            color=QColor(accent if values[net] else muted)
            scene.addEllipse(QRectF(x-3,y-3,6,6),QPen(color),QBrush(color)).setZValue(-0.5)
        for x,y in conflicts:
            color=QColor(STATUS[self.theme][1])
            item=scene.addEllipse(QRectF(x-5,y-5,10,10),QPen(color,1.4))
            item.setZValue(2)
            item.setToolTip("ابهام مسیر سیم؛ اتصال الکتریکی نیست" if self.fa else "Ambiguous wire contact; not an electrical connection")
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
                draw_gate(scene,gate.op,x,y,tuple(values[i] for i in gate.inputs),value,PALETTES[self.theme],self.symbol_style)
                label=gate.op
                if len(gate.inputs)>2 and gate.op in ("XOR","XNOR"):
                    label="ODD" if gate.op=="XOR" else "EVEN"
                text_at(label,x+25,y+HEIGHT+3,fg,10)
                text_at(name,x+25,y-17,muted,9)
            else:
                title=name[1:] if output else name
                color=accent if value else muted
                pin_x=x if output else x+WIDTH
                scene.addLine(pin_x,y+CENTER,x+(22 if output else 86),y+CENTER,QPen(QColor(color),1.8))
                body=QPainterPath()
                body.addRoundedRect(QRectF(x+22,y+CENTER-21,64,42),6,6)
                scene.addPath(body,QPen(QColor(color),1.5),QBrush(QColor(panel)))
                label=text_at(title,x+25,y+CENTER-20,fg,10)
                label.setToolTip(title)
                text_at(str(value),x+46,y+CENTER-1,color,12)
                scene.addEllipse(QRectF(pin_x-2,y+CENTER-2,4,4),QPen(QColor(color)),QBrush(QColor(color)))
        if self.editing:
            for name,pin,(x,y) in self.ports:
                dot=scene.addEllipse(QRectF(x-5,y-5,10,10),QPen(QColor(accent),1.5),QBrush(QColor(panel)))
                dot.setZValue(3)
                dot.setToolTip(f"{name}: " + (("مبدأ" if self.fa else "source") if pin<0 else (f"پایه {pin+1}" if self.fa else f"pin {pin+1}")))
        scene.setSceneRect(scene.itemsBoundingRect().adjusted(-40,-40,40,40))
        # This is a simultaneous change indication, not simulated propagation.
        if (self._last_circuit == circuit and self._last_route_key == route_key
                and not self.editing and not self.unrouted and not self.ambiguous
                and not self.reduced_motion and self.isVisible() and motion_allowed()):
            self._changed_paths = changed_routes(routes, self._last_values, values)
            if self._changed_paths:
                self._pulse = 1.0
                self._net_animation.start()
        self._last_circuit = circuit
        self._last_route_key = route_key
        self._last_values = dict(values)

    def clear_gesture(self):
        if self.preview is not None:
            self.graph.removeItem(self.preview)
            self.preview=None
        self.pending=None
        self.drag_node=None

    def set_editing(self, enabled):
        self.snap()
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
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft if self.fa else Qt.LayoutDirection.LeftToRight)
        self.history=[]
        self.dirty=False
        self.document=None
        self.selected_key=None
        self.setWindowTitle("Mano Studio — "+self.t("Logic Lab","آزمایشگاه منطق"))
        self.resize(1280,800)
        outer=QHBoxLayout(self);outer.setContentsMargins(12,12,12,12);outer.setSpacing(12)
        self.mode_tabs=MotionTabs()
        outer.addWidget(self.mode_tabs,1)
        combinational=QWidget()
        self.mode_tabs.addTab(combinational,self.t("Combinational","مدارهای ترکیبی"))
        self.sequential=SequentialView(parent.theme,self.fa)
        self.mode_tabs.addTab(self.sequential,self.t("Sequential","مدارهای ترتیبی"))
        self.memory_view=MemoryView(parent.theme,self.fa)
        self.memory_tabs=memory_tabs=MotionTabs()
        memory_tabs.addTab(self.memory_view,self.t("Memory chip","تراشه حافظه"))
        self.memory_array=MemoryArrayView(self.fa)
        memory_tabs.addTab(self.memory_array,self.t("Memory expansion","گسترش حافظه"))
        self.bus_view=BusView(parent.theme,self.fa)
        memory_tabs.addTab(self.bus_view,self.t("Register bus","گذرگاه ثبات‌ها"))
        self.databus=DatabusView(self.fa)
        memory_tabs.addTab(self.databus,self.t("RAM + registers","RAM و ثبات‌ها"))
        self.cache=CacheView(parent.theme,self.fa)
        memory_tabs.addTab(self.cache,self.t("Cache","حافظه نهان"))
        self.address_translation=AddressTranslationView(parent.theme,self.fa)
        memory_tabs.addTab(self.address_translation,self.t("CAM / Virtual memory","حافظه انجمنی / مجازی"))
        self.mode_tabs.addTab(memory_tabs,self.t("Memory & bus","حافظه و گذرگاه"))
        self.karnaugh=KarnaughView(self.fa)
        self.karnaugh.synthesize_requested.connect(self.build_karnaugh_circuit)
        self.mode_tabs.addTab(self.karnaugh,self.t("Karnaugh map","نقشه کارنو"))
        self.state_design=StateSynthesisView(self.fa)
        self.mode_tabs.addTab(self.state_design,self.t("State design","طراحی ماشین حالت"))
        self.navigation=NavigationRail(self.mode_tabs,parent.settings,"logic",self.t("DIGITAL LOGIC","منطق دیجیتال"),("logic","clock","registers","logic","clock"),self.fa)
        outer.insertWidget(0,self.navigation)
        layout=QVBoxLayout(combinational)
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
        library=QPushButton(self.t("Library / blocks","نمونه‌ها / بلوک‌ها"))
        menu=QMenu(library)
        menu.addAction(self.t("Insert circuit block","درج بلوک مدار"),self.insert_block)
        menu.addSeparator()
        chapters={}
        for sample in SAMPLES:
            chapter=sample["section"][:3]
            if chapter not in chapters:
                chapters[chapter]=menu.addMenu(self.t("Chapter "+str(int(chapter[1:])),
                    "فصل "+str(int(chapter[1:]))))
            chapters[chapter].addAction(sample["title"][self.fa],lambda checked=False,key=sample["id"]:self.open_sample(key))
        library.setMenu(menu)
        self.document_buttons.append(library)
        actions.addWidget(library)
        self.canvas_edit=QPushButton(self.t("Edit on canvas","ویرایش روی نقشه"))
        self.canvas_edit.setCheckable(True)
        self.canvas_edit.toggled.connect(self.toggle_canvas_edit)
        self.document_buttons.append(self.canvas_edit)
        actions.addWidget(self.canvas_edit)
        reset=QPushButton(self.t("Auto layout","چیدمان خودکار"))
        reset.clicked.connect(self.reset_layout)
        self.document_buttons.append(reset)
        actions.addWidget(reset)
        export_button=QPushButton(self.t("Export","خروجی"))
        export_menu=QMenu(export_button)
        export_menu.addAction(self.t("Schematic (SVG)","شماتیک (SVG)"),self.export_schematic)
        export_menu.addAction(self.t("Truth table (CSV)","جدول درستی (CSV)"),self.export_truth_table)
        export_button.setMenu(export_menu)
        self.document_buttons.append(export_button)
        actions.addWidget(export_button)
        actions.addStretch()
        layout.addLayout(actions)
        self.description=QLabel()
        self.description.setWordWrap(True)
        layout.addWidget(self.description)
        self.canvas_hint=QLabel()
        self.canvas_hint.setWordWrap(True)
        self.canvas_hint.setObjectName("muted")
        self.canvas_hint.hide()
        layout.addWidget(self.canvas_hint)
        self.input_widget=QWidget()
        self.input_grid=QGridLayout(self.input_widget)
        layout.addWidget(self.input_widget)
        self.summary=QLabel()
        self.summary.setWordWrap(True)
        self.summary.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        layout.addWidget(self.summary)
        self.route_warning=QLabel(self.t("Dashed wires or outlined contacts need clearer routing; move components or use Auto layout. Different-net crossings do not connect.","سیم‌های خط‌چین یا تماس‌های حلقه‌دار نیاز به اصلاح مسیر دارند؛ تقاطع سیگنال‌های متفاوت اتصال نیست."))
        self.route_warning.setWordWrap(True)
        self.route_warning.setProperty("state","error")
        self.route_warning.hide()
        layout.addWidget(self.route_warning)
        split=QSplitter(Qt.Orientation.Vertical)
        self.diagram=LogicDiagram(parent.theme,self.fa,parent.settings.value("gate_symbol_style","ansi"),
                                  reduced_motion=not parent.settings.value("lab_motion",True,type=bool))
        self.diagram.rewire.connect(self.rewire_pin)
        self.diagram.moved.connect(self.move_component)
        self.diagram.hint.connect(self.set_canvas_hint)
        split.addWidget(self.diagram)
        self.table=QTableWidget()
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.table.cellClicked.connect(self.choose_row)
        results=MotionTabs()
        results.addTab(self.table,self.t("Truth table","جدول درستی"))
        self.equations=QPlainTextEdit()
        self.equations.setReadOnly(True)
        self.equations.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.equations.setAccessibleName(self.t("Boolean equations","معادلات بولی"))
        results.addTab(self.equations,self.t("Boolean equations","معادلات بولی"))
        split.addWidget(results)
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
        self.mode_tabs.currentChanged.connect(self.refresh_karnaugh_source)

    def build_karnaugh_circuit(self):
        if self.stack.currentIndex()==1:
            QMessageBox.information(self,self.t("Apply first","ابتدا اعمال کنید"),
                self.t("Apply or cancel the staged circuit edit first.","ابتدا ویرایش مدار را اعمال یا لغو کنید."))
            return
        try:
            family=self.karnaugh.gate_family.currentData()
            values,form=self.karnaugh.values,self.karnaugh.form.currentData()
            if family=="MUX":
                document=synthesize_mux(values,form)
            else:
                document=synthesize(values,form)
                if family!="mixed":
                    document=universalize(document,family)
        except ValueError:
            QMessageBox.warning(self,self.t("Cannot build circuit","ساخت مدار ممکن نیست"),
                self.t("The selected realization exceeds the supported circuit limits or has invalid inputs.",
                       "پیاده‌سازی انتخاب‌شده از حدود مدار فراتر می‌رود یا ورودی نامعتبر دارد."))
            return
        except RuntimeError:
            QMessageBox.warning(self,self.t("Equivalence check failed","بررسی هم‌ارزی ناموفق بود"),
                self.t("The generated circuit was rejected; the current circuit is unchanged.",
                       "مدار تولیدشده رد شد؛ مدار فعلی بدون تغییر باقی ماند."))
            return
        answer=QMessageBox.question(self,self.t("Build circuit","ساخت مدار"),
            self.t("Replace the current circuit with this single-output circuit? Undo edit restores the previous circuit.",
                   "مدار جاری با این مدار تک‌خروجی جایگزین شود؟ واگرد ویرایش مدار قبلی را بازمی‌گرداند."),
            QMessageBox.StandardButton.Yes|QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No)
        if answer!=QMessageBox.StandardButton.Yes:
            return
        self.history.append((self.document,self.dirty))
        self.history=self.history[-30:]
        self.install_document(document,True)
        self.select_tool("gates")

    def refresh_karnaugh_source(self,*_):
        if self.mode_tabs.currentWidget() is self.karnaugh:
            self.karnaugh.set_source(self.circuit)

    def select_tool(self,route):
        if route in ("gates","sequential"):
            self.mode_tabs.setCurrentIndex(0 if route=="gates" else 1)
        elif route=="state-design":
            self.mode_tabs.setCurrentWidget(self.state_design)
        elif route=="karnaugh":
            self.mode_tabs.setCurrentWidget(self.karnaugh)
        elif route in ("cam","virtual-memory"):
            self.mode_tabs.setCurrentWidget(self.memory_tabs)
            self.memory_tabs.setCurrentWidget(self.address_translation)
            self.address_translation.tabs.setCurrentWidget(self.address_translation.cam if route=="cam" else self.address_translation.paging)
        elif route in ("memory-chip","memory-array","bus","cache"):
            self.mode_tabs.setCurrentWidget(self.memory_tabs)
            self.memory_tabs.setCurrentWidget({"memory-chip":self.memory_view,"memory-array":self.memory_array,"bus":self.bus_view,"cache":self.cache}[route])
        else:raise ValueError("Unknown logic route")

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

    def show_circuit(self, preserve=False, fit=True):
        old_inputs=getattr(self,"inputs",{}) if preserve else {}
        self.cancel_edit()
        self.undo_button.setEnabled(bool(self.history))
        self.inputs={name:old_inputs.get(name,0) for name in self.circuit.inputs}
        self.description.setText(self.circuit.explanation[self.fa]+"  |  "+self.t("Inputs / Outputs", "ورودی / خروجی")+f": {len(self.circuit.inputs)} / {len(self.circuit.outputs)}")
        while self.input_grid.count():
            item=self.input_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.buttons={}
        for i,name in enumerate(self.inputs):
            button=QPushButton()
            button.setCheckable(True)
            button.setChecked(bool(self.inputs[name]))
            button.toggled.connect(lambda checked,n=name:self.change(n,checked))
            self.buttons[name]=button
            self.input_grid.addWidget(button,i//6,i%6)
        self.equations.setPlainText("\n".join(circuit_equations(self.circuit)))
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
        if fit:
            self.diagram.fit()

    def set_canvas_hint(self, key):
        hints={
            "ready":self.t("Click a source pin, then a receiving pin. Drag a component to move it; Esc cancels.","روی پایه مبدأ و سپس پایه مقصد کلیک کنید. اجزا را بکشید؛ Esc لغو می‌کند."),
            "source":self.t("Choose a receiving pin to replace its connection.","برای جایگزینی اتصال، پایه مقصد را انتخاب کنید."),
            "overlap":self.t("Components cannot overlap.","اجزا نباید روی هم قرار بگیرند."),
        }
        self.canvas_hint.setText(hints.get(key,key))

    def toggle_canvas_edit(self,enabled):
        self.diagram.set_editing(enabled)
        self.canvas_hint.setVisible(enabled)
        self.set_canvas_hint("ready")
        self.refresh()

    def commit_canvas(self,document):
        if document==self.document:
            self.set_canvas_hint("ready")
            return
        self.history.append((self.document,self.dirty))
        self.history=self.history[-30:]
        self.install_document(document,True,preserve=True,fit=False)
        self.set_canvas_hint("ready")

    def rewire_pin(self,source,target,pin):
        try:
            document=self.document.reconnect(source,target,pin)
            if document!=self.document:
                document=document.with_positions(self.diagram.positions)
        except ValueError as exc:
            self.set_canvas_hint(error_text(exc,self.fa))
            return
        self.commit_canvas(document)

    def move_component(self,name,x,y):
        positions=dict(self.diagram.positions)
        if name not in positions:
            return
        positions[name]=(x,y)
        try:
            document=self.document.with_positions(positions)
        except ValueError as exc:
            self.set_canvas_hint(error_text(exc,self.fa))
            return
        self.commit_canvas(document)

    def reset_layout(self):
        self.commit_canvas(self.document.with_positions({}))
        self.diagram.fit()

    def confirm_discard(self):
        if not self.dirty:
            return True
        return QMessageBox.question(self,self.t("Unsaved circuit","مدار ذخیره‌نشده"),
            self.t("Discard unsaved circuit changes?","تغییرات ذخیره‌نشده مدار حذف شوند؟"),
            QMessageBox.StandardButton.Discard|QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Cancel)==QMessageBox.StandardButton.Discard

    def edit_circuit(self):
        self.canvas_edit.setChecked(False)
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

    def install_document(self,document,dirty,preserve=False,fit=True):
        circuit=document.compile()
        self.document,self.circuit=document,circuit
        self.dirty=dirty
        self.selected_key="custom"
        self.selector.blockSignals(True)
        self.selector.setCurrentIndex(self.selector.findData("custom"))
        self.selector.blockSignals(False)
        self.pin_count.setEnabled(False)
        self.show_circuit(preserve=preserve,fit=fit)

    def apply_document(self,document):
        names=set(document.inputs)|{g.output for g in document.gates}|{"@"+n for n,_ in document.outputs}
        # Retain manual placement for surviving components, without adding stale coordinates.
        document=document.with_positions({n:(x,y) for n,x,y in self.document.positions if n in names})
        if document!=self.document:
            self.history.append((self.document,self.dirty))
            self.history=self.history[-30:]
            self.install_document(document,True,preserve=True)
        else:
            self.cancel_edit()

    def undo_edit(self):
        if self.history:
            document,dirty=self.history.pop()
            self.install_document(document,dirty,preserve=True)

    def insert_block(self):
        if self.stack.currentIndex()==1:
            return
        dialog=BlockDialog(self.document,self.fa,self)
        if dialog.exec()==QDialog.DialogCode.Accepted and dialog.result_document is not None:
            self.history.append((self.document,self.dirty))
            self.history=self.history[-30:]
            self.install_document(dialog.result_document,True,preserve=True)

    def open_sample(self,key):
        if self.stack.currentIndex()==1:
            return
        document=load_sample(key)
        if not self.confirm_discard():
            return
        self.history.append((self.document,self.dirty))
        self.history=self.history[-30:]
        self.install_document(document,False)
        sample=next(s for s in SAMPLES if s["id"]==key)
        self.description.setText(sample["title"][self.fa]+" · "+sample["task"][self.fa])

    def open_circuit(self):
        if not self.confirm_discard():
            return
        name,_=QFileDialog.getOpenFileName(self,self.t("Open circuit","باز کردن مدار"),"","Mano Studio (*.mano);;Legacy circuit (*.mano-logic.json);;JSON (*.json)")
        if not name:
            return
        try:
            document=load_circuit(name)
        except (OSError,UnicodeError,ValueError) as exc:
            QMessageBox.warning(self,self.t("Invalid circuit","مدار نامعتبر"),error_text(exc,self.fa))
            return
        self.history.clear()
        self.install_document(document,False)

    def save_circuit(self):
        if self.stack.currentIndex()==1:
            QMessageBox.information(self,self.t("Apply first","ابتدا اعمال کنید"),
                self.t("Apply or cancel the staged edit before saving.","پیش از ذخیره، ویرایش را اعمال یا لغو کنید."))
            return
        name,_=QFileDialog.getSaveFileName(self,self.t("Save circuit","ذخیره مدار"),"circuit.mano","Mano Studio (*.mano);;Legacy circuit (*.mano-logic.json);;JSON (*.json)")
        if not name:
            return
        path=Path(name)
        if not path.suffix:
            path=path.with_suffix(".mano")
        try:
            save_circuit(path,self.document)
        except (OSError,ValueError) as exc:
            QMessageBox.warning(self,self.t("Cannot save","ذخیره ناموفق"),error_text(exc,self.fa))
            return
        self.dirty=False
        # Undo after saving changes the document relative to the saved file.
        self.history=[(document,True) for document,_ in self.history]

    def write_truth_table(self,path):
        with Path(path).open("w",encoding="utf-8-sig",newline="") as stream:
            writer=csv.writer(stream)
            writer.writerow(list(self.circuit.inputs)+[n for n,_ in self.circuit.outputs])
            writer.writerows(bits+outputs for bits,outputs in self.rows)

    def export_truth_table(self):
        name,_=QFileDialog.getSaveFileName(self,self.t("Export truth table","خروجی جدول درستی"),"truth-table.csv","CSV (*.csv)")
        if name:
            try:
                self.write_truth_table(Path(name) if Path(name).suffix else Path(name).with_suffix(".csv"))
            except OSError as exc:
                QMessageBox.warning(self,self.t("Export failed","خروجی ناموفق"),error_text(exc,self.fa))

    def write_schematic(self,path):
        # Exclude temporary editing handles and previews from the exported diagram.
        was_editing=self.diagram.editing
        self.diagram.set_editing(False)
        try:
            self.refresh()
            bounds=self.diagram.graph.sceneRect()
            if bounds.width()>70000 or bounds.height()>70000:
                raise ValueError("Schematic export dimensions too large.")
            generator=QSvgGenerator()
            generator.setFileName(str(path))
            generator.setSize(QSize(max(1,int(bounds.width())),max(1,int(bounds.height()))))
            generator.setViewBox(bounds)
            generator.setTitle("Mano Studio — digital schematic")
            painter=QPainter()
            if not painter.begin(generator):
                raise OSError("Cannot create SVG file.")
            try:
                self.diagram.graph.render(painter,bounds,bounds)
            finally:
                painter.end()
        finally:
            self.diagram.set_editing(was_editing)
            self.refresh()

    def export_schematic(self):
        name,_=QFileDialog.getSaveFileName(self,self.t("Export schematic","خروجی شماتیک"),"circuit.svg","SVG (*.svg)")
        if name:
            try:
                self.write_schematic(Path(name) if Path(name).suffix else Path(name).with_suffix(".svg"))
            except (OSError,ValueError) as exc:
                QMessageBox.warning(self,self.t("Export failed","خروجی ناموفق"),error_text(exc,self.fa))

    def done(self,result):
        if self.stack.currentIndex()==1 and QMessageBox.question(self,self.t("Unapplied edits","ویرایش اعمال‌نشده"),self.t("Discard staged edits?","ویرایش‌های اعمال‌نشده حذف شوند؟"),QMessageBox.StandardButton.Discard|QMessageBox.StandardButton.Cancel,QMessageBox.StandardButton.Cancel)!=QMessageBox.StandardButton.Discard:
            return
        if self.confirm_discard() and self.databus.confirm_close() and self.state_design.confirm_close():
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
        self.diagram.draw(self.circuit,values,self.document.positions)
        self.route_warning.setVisible(bool(self.diagram.unrouted or self.diagram.ambiguous))
        bits=tuple(self.inputs.values())
        row=next(i for i,(inputs,_) in enumerate(self.rows) if inputs==bits)
        self.table.selectRow(row)
