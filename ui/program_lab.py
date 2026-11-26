"""Live program workspace: actual assembler and CPU, not the fixed demo."""
from pathlib import Path
from ui.motion import MotionTabs
from ui.navigation_rail import NavigationRail
import csv
from memory_inspector import parse_address, page_addresses, memory_rows
import memory_export
from memory_navigation import adjacent_page
from memory_refresh import refresh_plan, row_for_address
from word_decode import decode_word
from memory_edit import parse_word, write_word
from PySide6.QtWidgets import QInputDialog
from PySide6.QtCore import QTimer, QSignalBlocker
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QPlainTextEdit, QTableWidget, QTableWidgetItem, QHeaderView,
    QAbstractItemView, QSplitter, QSpinBox, QLineEdit, QTabWidget, QFileDialog, QMessageBox, QWidget, QMenu)
from PySide6.QtCore import Qt
from PySide6.QtGui import QTextCursor
from execution_history import ExecutionHistory
from ui.arithmetic_view import ArithmeticView
from ui.data_codes_view import DataCodesView
from ui.cycle_view import CycleView
from ui.microprogram_view import MicroprogramView
from ui.cpu_organization_view import OrganizationView
from ui.pipeline_view import PipelineView
from ui.vector_pipeline_view import VectorPipelineView
from ui.interleaving_view import InterleavingView
from ui.floating_pipeline_view import FloatPipelineView
from ui.io_organization_view import IOOrganizationView
from ui.multiprocessor_view import MultiprocessorView
from ui.crossbar_view import CrossbarView
from ui.synchronization_view import SynchronizationView
from ui.coherence_view import CoherenceView
from ui.omega_view import OmegaView
from ui.localization import error_text
from assembler import assemble
from simulator import CPU
import cpu_session
import cpu_documents
import mano_file
from cpu_guard import CpuGuard
from replacement_guard import allow_replace
from program_samples import SAMPLES, load_sample
from ui.workspace import code_editor
from ui.datapath_view import DatapathView

EXAMPLE = """ORG 000
LDA A
ADD B
STA C
HLT
A, DEC 5
B, DEC 3
C, HEX 0000
END"""


class ProgramLab(QDialog):
    def __init__(self, parent, assembly=""):
        super().__init__(parent)
        self.fa = parent.language == "fa"
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft if self.fa else Qt.LayoutDirection.LeftToRight)
        self.setWindowTitle("Mano Studio — " + self.t("Computer", "کامپیوتر"))
        self.resize(1280, 800)
        self.cpu = None
        self.assembled_source = None
        self.inspected_address = None
        self.memory_snapshot = ()
        self.program = None
        self.steps = 0
        self.history = None
        self.break_resume = None
        self.visible_trace=[]
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.run_tick)
        shell=QHBoxLayout(self);shell.setContentsMargins(12,12,12,12);shell.setSpacing(12)
        content=QWidget();layout=QVBoxLayout(content);layout.setContentsMargins(0,0,0,0);layout.setSpacing(8)
        shell.addWidget(content,1)
        intro = QLabel(self.t("Assemble and execute your own program, one instruction at a time.",
            "برنامه خود را اسمبل کنید و اجرای هر دستور را مرحله‌به‌مرحله ببینید."))
        intro.setWordWrap(True)
        layout.addWidget(intro)
        panes = QSplitter(Qt.Orientation.Horizontal)
        self.source = code_editor(theme=parent.theme)
        self.source.setPlainText(assembly or EXAMPLE)
        self.machine = code_editor(True, theme=parent.theme)
        panes.addWidget(self.source)
        panes.addWidget(self.machine)
        panes.setSizes([500, 500])
        layout.addWidget(panes, 2)
        controls = QHBoxLayout()
        self.examples_button = QPushButton(self.t("Saved examples", "نمونه‌های ذخیره‌شده"))
        menu = QMenu(self.examples_button)
        for sample in SAMPLES:
            menu.addAction(sample.title[self.fa], lambda checked=False, key=sample.key: self.open_saved_sample(key))
        self.examples_button.setMenu(menu)
        controls.addWidget(self.examples_button)
        self.session_button = QPushButton(self.t("Session", "جلسه اجرا"))
        session_menu = QMenu(self.session_button)
        session_menu.addAction(self.t("Open session or draft", "باز کردن جلسه یا پیش‌نویس"), self.open_cpu_session)
        session_menu.addAction(self.t("Save CPU session", "ذخیره جلسه پردازنده"), self.save_cpu_session)
        self.session_button.setMenu(session_menu)
        controls.addWidget(self.session_button)
        self.edit_source_button = QPushButton(self.t("Edit source", "ویرایش کد"))
        self.edit_source_button.clicked.connect(self.begin_source_edit)
        controls.addWidget(self.edit_source_button)
        for en, fa, slot in [("Assemble / Reset","اسمبل و بازنشانی",self.reset_program),
            ("Back","گام قبل",self.back),("Step","گام بعد",self.step),("Run","اجرا",self.run),
            ("Pause","توقف موقت",self.pause)]:
            b = QPushButton(self.t(en,fa))
            b.clicked.connect(slot)
            controls.addWidget(b)
            if en=="Back":self.back_button=b
        self.speed = QSpinBox()
        self.speed.setRange(100, 2000)
        self.speed.setValue(600)
        self.speed.setSuffix(" ms")
        self.speed.valueChanged.connect(self.timer.setInterval)
        controls.addWidget(self.speed)
        cpu_controls=QWidget();cpu_controls.setLayout(controls)
        layout.addWidget(cpu_controls)
        lower = QSplitter(Qt.Orientation.Horizontal)
        self.registers = QTableWidget(0, 2)
        self.registers.setHorizontalHeaderLabels([self.t("Register","ثبات"), self.t("Value (HEX)","مقدار هگز")])
        self.memory = QTableWidget(0, 3)
        self.memory.setHorizontalHeaderLabels([self.t("Address","آدرس"), self.t("Word (HEX)","کلمه هگز"),
            self.t("If instruction","اگر دستور باشد")])
        for table in (self.registers,self.memory):
            table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
            table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            lower.addWidget(table)
        self.inspector=MotionTabs()
        self.datapath=DatapathView(parent.theme, parent.settings.value("reduced_motion", False, type=bool) or not parent.settings.value("lab_motion", True, type=bool), fa=self.fa)
        self.inspector.addTab(self.datapath,self.t("Live view","نمای زنده"))
        memory_panel = QWidget()
        memory_layout = QVBoxLayout(memory_panel)
        memory_layout.setContentsMargins(0,0,0,0)
        memory_tools = QHBoxLayout()
        self.memory_address = QLineEdit()
        self.memory_address.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.memory_address.setPlaceholderText("000–FFF")
        self.memory_address.setAccessibleName(self.t("Memory address", "آدرس حافظه"))
        self.memory_address.returnPressed.connect(self.inspect_memory)
        self.memory.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.memory.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.memory.currentCellChanged.connect(self.select_memory_address)
        self.memory.cellClicked.connect(self.select_memory_address)
        self.memory_address.setToolTip(self.t("Type a HEX address or select a memory row.",
            "آدرس هگز وارد کنید یا یک ردیف حافظه را انتخاب کنید."))
        memory_tools.addWidget(self.memory_address)
        self.inspect_memory_button = QPushButton(self.t("Inspect address", "مشاهده آدرس"))
        self.inspect_memory_button.clicked.connect(self.inspect_memory)
        memory_tools.addWidget(self.inspect_memory_button)
        self.previous_memory_button = QPushButton(self.t("Previous page", "صفحه قبل"))
        self.previous_memory_button.clicked.connect(lambda: self.move_memory_page(-1))
        memory_tools.addWidget(self.previous_memory_button)
        self.next_memory_button = QPushButton(self.t("Next page", "صفحه بعد"))
        self.next_memory_button.clicked.connect(lambda: self.move_memory_page(1))
        memory_tools.addWidget(self.next_memory_button)
        memory_layout.addLayout(memory_tools)
        memory_actions = QHBoxLayout()
        self.clear_memory_button = QPushButton(self.t("Accessed only", "فقط آدرس‌های استفاده‌شده"))
        self.clear_memory_button.clicked.connect(self.clear_memory_page)
        memory_actions.addWidget(self.clear_memory_button)
        self.export_memory_button = QPushButton(self.t("Export CSV", "خروجی CSV"))
        self.export_memory_button.clicked.connect(self.export_memory)
        memory_actions.addWidget(self.export_memory_button)
        self.edit_memory_button = QPushButton(self.t("Edit word", "ویرایش کلمه"))
        self.edit_memory_button.clicked.connect(self.edit_memory)
        memory_actions.addWidget(self.edit_memory_button)
        self.memory_page_label = QLabel()
        memory_actions.addWidget(self.memory_page_label)
        self.memory_page_label.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        memory_actions.addStretch(1)
        memory_layout.addLayout(memory_actions)
        self.memory.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.registers.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        memory_layout.addWidget(lower,1)
        self.inspector.addTab(memory_panel,self.t("Registers & memory","ثبات‌ها و حافظه"))
        trace_page=QWidget()
        trace_layout=QVBoxLayout(trace_page)
        trace_tools=QHBoxLayout()
        self.break_address=QLineEdit()
        self.break_address.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.break_address.setPlaceholderText(self.t("Breakpoint HEX","نقطه توقف هگز"))
        trace_tools.addWidget(self.break_address)
        for en,fa,fn in [("Toggle breakpoint","تغییر نقطه توقف",self.toggle_breakpoint),
                         ("Export trace","خروجی رد اجرا",self.export_trace)]:
            button=QPushButton(self.t(en,fa))
            button.clicked.connect(fn)
            trace_tools.addWidget(button)
        trace_layout.addLayout(trace_tools)
        self.break_label=QLabel()
        trace_layout.addWidget(self.break_label)
        self.trace=QTableWidget(0,7)
        self.trace.setHorizontalHeaderLabels(["#","PC",self.t("Word","کلمه"),"OP","EA","AC",self.t("Next PC","PC بعدی")])
        self.trace.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.trace.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.trace.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.trace.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.trace.cellClicked.connect(self.trace_selected)
        trace_layout.addWidget(self.trace)
        self.inspector.addTab(trace_page,self.t("Debugger","اشکال‌زدا"))
        alu_page=QWidget()
        alu_layout=QVBoxLayout(alu_page)
        use_registers=QPushButton(self.t("Use AC, DR & E","استفاده از AC، DR و E"))
        use_registers.clicked.connect(self.use_registers)
        alu_layout.addWidget(use_registers)
        self.arithmetic=ArithmeticView(self.fa)
        alu_layout.addWidget(self.arithmetic)
        self.inspector.addTab(alu_page,self.t("Data & ALU","داده و ALU"))
        self.codes=DataCodesView(self.fa)
        self.inspector.addTab(self.codes,self.t("Data codes","کدهای داده"))
        self.cycles=CycleView(self.fa,self.microstep,self.microback)
        self.inspector.addTab(self.cycles,self.t("Instruction cycle","چرخه دستور"))
        self.microprogram=MicroprogramView(self.fa)
        self.inspector.addTab(self.microprogram,self.t("Microprogram","ریزبرنامه"))
        self.organization=OrganizationView(self.fa)
        self.inspector.addTab(self.organization,self.t("CPU organization","سازمان CPU"))
        self.pipeline=PipelineView(self.fa)
        self.vector_pipeline=VectorPipelineView(self.fa)
        self.pipeline_tabs=pipeline_tabs=MotionTabs()
        pipeline_tabs.addTab(self.pipeline,self.t("Instruction pipeline","خط لوله دستورات"))
        pipeline_tabs.addTab(self.vector_pipeline,self.t("Vector / matrix","بردار / ماتریس"))
        self.interleaving=InterleavingView(self.fa)
        pipeline_tabs.addTab(self.interleaving,self.t("Memory banks","بانک‌های حافظه"))
        self.float_pipeline=FloatPipelineView(self.fa)
        pipeline_tabs.addTab(self.float_pipeline,self.t("Floating pipeline","خط لوله ممیز شناور"))
        self.inspector.addTab(pipeline_tabs,self.t("Pipeline","خط لوله"))
        self.io_organization=IOOrganizationView(self.fa,parent.theme)
        self.inspector.addTab(self.io_organization,self.t("I/O organization","سازمان ورودی/خروجی"))
        self.multiprocessor=MultiprocessorView(parent.theme,self.fa)
        self.crossbar=CrossbarView(parent.theme,self.fa)
        self.multiprocessor_tabs=MotionTabs()
        self.multiprocessor_tabs.addTab(self.multiprocessor,self.t("Shared bus","گذرگاه مشترک"))
        self.multiprocessor_tabs.addTab(self.crossbar,self.t("Crossbar","اتصال متقاطع"))
        self.synchronization=SynchronizationView(parent.theme,self.fa)
        self.multiprocessor_tabs.addTab(self.synchronization,self.t("Synchronization","همگام‌سازی"))
        self.coherence=CoherenceView(parent.theme,self.fa)
        self.multiprocessor_tabs.addTab(self.coherence,self.t("Cache coherence","هماهنگی کش"))
        self.omega=OmegaView(parent.theme,self.fa)
        self.multiprocessor_tabs.addTab(self.omega,self.t("Omega network","شبکه امگا"))
        self.inspector.addTab(self.multiprocessor_tabs,self.t("Multiprocessors","چندپردازنده‌ها"))
        layout.addWidget(self.inspector, 2)
        io = QHBoxLayout()
        self.input = QLineEdit()
        self.input.setPlaceholderText(self.t("Input byte (00–FF)","بایت ورودی (00–FF)"))
        self.input.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        io.addWidget(self.input)
        for en,fa,slot in [("Send input","ارسال ورودی",self.send_input),
                           ("Read output","خواندن خروجی",self.read_output)]:
            b=QPushButton(self.t(en,fa))
            b.clicked.connect(slot)
            io.addWidget(b)
        cpu_io=QWidget();cpu_io.setLayout(io)
        layout.addWidget(cpu_io)
        self.status = QLabel()
        self.status.setWordWrap(True)
        layout.addWidget(self.status)
        self.cpu_widgets=(intro,panes,cpu_controls,cpu_io,self.status)
        self.tool_pages={"live":self.datapath,"register-memory":memory_panel,"debugger":trace_page,
                         "alu":alu_page,"codes":self.codes,"cycles":self.cycles,
                         "microprogram":self.microprogram,"organization":self.organization,
                         "pipeline":pipeline_tabs,"io":self.io_organization,"multiprocessor":self.multiprocessor_tabs}
        self.navigation=NavigationRail(self.inspector,parent.settings,'computer',self.t('COMPUTER','کامپیوتر'),
            ('cpu','registers','debug','alu','codes','clock','microcode','organization','pipeline','io','network'),self.fa)
        shell.insertWidget(0,self.navigation)
        self.datapath.focus.toggled.connect(self.update_cpu_context)
        self.inspector.currentChanged.connect(self.update_cpu_context)
        self.source.textChanged.connect(self.invalidate)
        self.load()
        self.cpu_guard = CpuGuard(self.source.toPlainText(), self.cpu, self.history)
        self.update_cpu_context()

    def update_cpu_context(self,*_):
        page=self.inspector.currentWidget()
        visible=page in tuple(self.tool_pages[key] for key in ("live","register-memory","debugger","cycles"))
        focused=page is self.datapath and self.datapath.focus.isChecked()
        # Arithmetic has its own operands and an explicit AC/DR/E import.
        # Give it the full inspector area; retain the CPU and program unchanged.
        if not visible:self.pause()
        for widget in self.cpu_widgets:widget.setVisible(visible and not focused)
        if focused:
            # Preserve execution controls while maximizing the visualization.
            self.cpu_widgets[2].show()

    def select_tool(self,route):
        """Stable learning route IDs, independent of displayed tab titles."""
        if route in self.tool_pages:
            self.inspector.setCurrentWidget(self.tool_pages[route])
            if route=="multiprocessor":self.multiprocessor_tabs.setCurrentWidget(self.multiprocessor)
            if route=="pipeline":self.pipeline_tabs.setCurrentWidget(self.pipeline)
            if route=="microprogram":self.microprogram.detail_tabs.setCurrentIndex(0)
            if route=="alu":self.arithmetic.op.setCurrentIndex(0)
        elif route in ("crossbar","synchronization","coherence","omega"):
            self.inspector.setCurrentWidget(self.multiprocessor_tabs)
            self.multiprocessor_tabs.setCurrentWidget({"crossbar":self.crossbar,"synchronization":self.synchronization,"coherence":self.coherence,"omega":self.omega}[route])
        elif route=="microbuilder":
            self.inspector.setCurrentWidget(self.microprogram)
            self.microprogram.detail_tabs.setCurrentWidget(self.microprogram.builder)
        elif route in ("general-registers","stacks","addressing","formats"):
            self.inspector.setCurrentWidget(self.organization)
            self.organization.tabs.setCurrentIndex(("general-registers","stacks","addressing","formats").index(route))
        elif route in ("vector","interleaving","floating-pipeline"):
            self.inspector.setCurrentWidget(self.pipeline_tabs)
            self.pipeline_tabs.setCurrentWidget({"vector":self.vector_pipeline,"interleaving":self.interleaving,"floating-pipeline":self.float_pipeline}[route])
        elif route in ("handshake","interrupt","dma","fifo","serial"):
            self.inspector.setCurrentWidget(self.io_organization)
            self.io_organization.tabs.setCurrentIndex(("handshake","interrupt","dma","fifo","serial").index(route))
        elif route in ("booth","division","decimal","floating"):
            self.inspector.setCurrentWidget(self.tool_pages["alu"])
            data={"booth":"booth","division":"divide","decimal":"bcdadd","floating":"fpdecode"}[route]
            self.arithmetic.op.setCurrentIndex(self.arithmetic.op.findData(data))
        else:raise ValueError("Unknown computer route")
        self.update_cpu_context()

    def t(self,en,fa):
        return fa if self.fa else en

    def replace_source(self, source):
        # Internal validated replacements must not trigger the live-edit guard.
        with QSignalBlocker(self.source):
            self.source.setPlainText(source)

    def set_source_locked(self, locked):
        self.source.setReadOnly(locked)
        self.edit_source_button.setEnabled(locked)

    def invalidate(self):
        self.pause()
        if self.cpu is not None:
            # Even a programmatic edit must not detach the live CPU from its source.
            if self.source.toPlainText() != self.assembled_source:
                self.replace_source(self.assembled_source)
                self.status.setText(self.t("Choose Edit source before changing a live program.",
                                           "برای تغییر برنامه در حال اجرا، ویرایش کد را انتخاب کنید."))
            return
        self.status.setText(self.t("Source changed. Assemble again.","کد تغییر کرد؛ دوباره اسمبل کنید."))

    def clear_execution(self):
        self.pause()
        self.cpu = self.program = None
        self.assembled_source = None
        self.reset_memory_page()
        self.history = None
        self.break_resume = None
        self.steps=0
        self.refresh_trace()
        self.machine.clear()
        self.datapath.set_state(None)
        self.registers.setRowCount(0)
        self.refresh_memory()
        self.set_source_locked(False)

    def begin_source_edit(self):
        if self.cpu is not None and not self.confirm_close():
            return False
        self.clear_execution()
        self.source.setFocus()
        self.status.setText(self.t("Edit assembly, then Assemble / Reset.",
                                   "اسمبلی را ویرایش کنید و سپس اسمبل و بازنشانی را بزنید."))
        return True

    def is_dirty(self):
        return self.cpu_guard.is_dirty(self.source.toPlainText(), self.cpu, self.history)

    def mark_saved(self):
        self.cpu_guard.mark_saved(self.source.toPlainText(), self.cpu, self.history)

    def confirm_close(self):
        self.pause()
        if not self.is_dirty():
            return True
        choice = QMessageBox.question(self, self.t("Unsaved CPU workspace", "فضای پردازنده ذخیره‌نشده"),
            self.t("Save the current program and execution state before continuing?",
                   "برنامه و وضعیت اجرای فعلی پیش از ادامه ذخیره شوند؟"),
            QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Save)
        if choice == QMessageBox.StandardButton.Save:
            return self.save_cpu_session()
        return choice == QMessageBox.StandardButton.Discard

    def confirm_replace(self):
        self.pause()
        def confirm_clean():
            return QMessageBox.question(self, self.t("Replace program?", "جایگزینی برنامه؟"),
                self.t("Replace the current program and execution state?",
                       "برنامه و وضعیت اجرای فعلی جایگزین شوند؟"),
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes
        return allow_replace(self.is_dirty(), bool(self.cpu is not None or self.source.toPlainText()),
                             self.confirm_close, confirm_clean)

    def reset_program(self):
        if self.cpu is not None and not self.confirm_close():
            return
        self.load()

    def save_cpu_session(self):
        self.pause()
        if self.cpu is not None and (self.history is None or self.cpu.in_progress):
            QMessageBox.warning(self, self.t("Cannot save session", "ذخیره جلسه ناموفق"),
                self.t("Assemble and finish or rewind the current instruction before saving.",
                       "ابتدا اسمبل کنید و دستور جاری را کامل کنید یا به ابتدای آن بازگردید."))
            return False
        draft = self.cpu is None
        title = self.t("Save assembly draft", "ذخیره پیش‌نویس اسمبلی") if draft else self.t("Save CPU session", "ذخیره جلسه پردازنده")
        name, _ = QFileDialog.getSaveFileName(self, title,
            "draft.mano" if draft else "cpu.mano", self.t("Mano Studio (*.mano)", "مانو استودیو (*.mano)"))
        if not name:
            return False
        path = Path(name)
        if not path.suffix:
            path = path.with_suffix(".mano")
        if path.suffix.lower() != ".mano":
            QMessageBox.warning(self, self.t("Cannot save session", "ذخیره جلسه ناموفق"),
                self.t("Use the .mano extension.", "از پسوند .mano استفاده کنید."))
            return False
        try:
            if draft:
                mano_file.save(path, "asm", self.source.toPlainText())
            else:
                cpu_session.save(path, self.source.toPlainText(), self.cpu, self.history.steps, self.history.breakpoints)
        except (OSError, ValueError):
            QMessageBox.warning(self, self.t("Cannot save session", "ذخیره جلسه ناموفق"),
                self.t("Session could not be saved.", "جلسه ذخیره نشد."))
            return False
        self.mark_saved()
        self.status.setText(self.t("Assembly draft saved.", "پیش‌نویس اسمبلی ذخیره شد.") if draft else self.t("CPU session saved.", "جلسه پردازنده ذخیره شد."))
        return True

    def install_cpu_session(self, restored):
        source, program, cpu, steps, breaks = restored
        self.pause()
        self.replace_source(source)
        self.program, self.cpu = program, cpu
        self.reset_memory_page()
        self.assembled_source = self.source.toPlainText()
        self.set_source_locked(True)
        self.history = ExecutionHistory(cpu)
        self.history.steps = self.steps = steps
        self.history.breakpoints = breaks
        self.break_resume = None
        self.addresses = set(program.words) | {a for a, w in enumerate(cpu.memory) if w} | {cpu.pc}
        self.machine.setPlainText(program.listing())
        self.refresh()
        self.select_address(cpu.pc)
        self.mark_saved()
        self.status.setText(self.t("Session restored; reverse history starts here.",
                                   "جلسه بازیابی شد؛ تاریخچه بازگشت از اینجا آغاز می‌شود."))

    def open_cpu_session(self):
        self.pause()
        name, _ = QFileDialog.getOpenFileName(self, self.t("Open session or draft", "باز کردن جلسه یا پیش‌نویس"),
            "", self.t("Mano Studio (*.mano)", "مانو استودیو (*.mano)"))
        if not name:
            return False
        try:
            kind, restored = cpu_documents.read(name, cpu_session.restore)
        except (OSError, ValueError):
            QMessageBox.warning(self, self.t("Cannot open session", "باز کردن جلسه ناموفق"),
                self.t("Invalid session. Current program is unchanged.", "جلسه نامعتبر است؛ برنامه فعلی تغییر نکرد."))
            return False
        if not self.confirm_replace():
            return False
        if kind == "asm":
            self.clear_execution()
            self.replace_source(restored)
            self.mark_saved()
            self.source.setFocus()
            self.status.setText(self.t("Draft opened; assemble when ready.", "پیش‌نویس باز شد؛ پس از تکمیل اسمبل کنید."))
        else:
            self.install_cpu_session(restored)
        return True

    def open_saved_sample(self, key):
        # Validate before changing the live program or any execution state.
        try:
            sample, source = load_sample(key)
            if not assemble(source).ok:
                raise ValueError("Invalid saved program")
        except (OSError, ValueError):
            QMessageBox.warning(self, self.t("Cannot open example", "باز کردن نمونه ناموفق بود"),
                self.t("The saved program is invalid or unreadable. Current program is unchanged.",
                       "برنامه ذخیره‌شده نامعتبر یا خواندنی نیست. برنامه فعلی تغییر نکرد."))
            return False
        if not self.confirm_replace():
            return False
        self.replace_source(source)
        self.load()
        self.mark_saved()
        self.status.setText(sample.task[self.fa])
        return True

    def example(self):
        if not self.confirm_close():
            return
        self.replace_source(EXAMPLE)
        self.load()
        self.mark_saved()

    def load(self):
        self.pause()
        self.program = assemble(self.source.toPlainText())
        self.reset_memory_page()
        self.assembled_source = None
        self.set_source_locked(False)
        self.cpu = None
        self.history = None
        self.break_resume = None
        self.steps = 0
        self.refresh_trace()
        if not self.program.ok:
            self.datapath.set_state(None)
            self.machine.setPlainText("\n".join(f"{e.line}: {error_text(e.message,self.fa)}" for e in self.program.errors))
            self.status.setText(self.t("Assembly failed.","اسمبل ناموفق بود."))
            self.registers.setRowCount(0)
            self.refresh_memory()
            return
        if not self.program.words:
            self.machine.clear()
            self.datapath.set_state(None)
            self.registers.setRowCount(0)
            self.refresh_memory()
            self.status.setText(self.t("No memory words assembled. Edit the draft.",
                                       "هیچ کلمه‌ای اسمبل نشد؛ پیش‌نویس را ویرایش کنید."))
            return
        self.machine.setPlainText(self.program.listing())
        self.cpu = CPU(self.program.words, self.program.entry)
        self.assembled_source = self.source.toPlainText()
        self.set_source_locked(True)
        self.history = ExecutionHistory(self.cpu)
        self.addresses = set(self.program.words)
        self.refresh()
        self.status.setText(self.t("Ready.","آماده."))

    def refresh(self,event=None):
        self.datapath.set_state(self.cpu,self.cpu.pending_event or event)
        self.refresh_trace()
        values = self.cpu.registers()
        self.registers.setRowCount(len(values))
        for row,(name,value) in enumerate(values.items()):
            width = 3 if name in ("PC","AR") else 4 if name in ("AC","DR","IR","TR") else 2 if name in ("INPR","OUTR") else 1
            self.registers.setItem(row,0,QTableWidgetItem(name))
            item = QTableWidgetItem(f"{value:0{width}X}")
            if event and event.before.get(name) != value:
                from PySide6.QtGui import QColor
                item.setBackground(QColor(80,145,185,70))
            self.registers.setItem(row,1,item)
        if event:
            self.addresses.update(a for g in event.microevents for a,_ in g.reads)
            self.addresses.update(a for a,old,new in event.writes)
            if event.effective_address is not None:
                self.addresses.add(event.effective_address)
        self.refresh_memory()

    def reset_memory_page(self):
        self.inspected_address = None
        self.memory_address.clear()
        self.memory_page_label.clear()

    def move_memory_page(self, direction):
        if self.cpu is None:
            return False
        address = adjacent_page(self.inspected_address, direction)
        if address is None:
            return False
        self.memory_address.setText(f"{address:03X}")
        return self.inspect_memory()

    def select_memory_address(self, row, *_columns):
        """An explicit table selection updates the edit target, not the page."""
        if self.cpu is None or not 0 <= row < len(self.memory_snapshot):
            return
        self.memory_address.setText(f"{self.memory_snapshot[row][0]:03X}")

    def refresh_memory(self):
        # Model-driven selection and repaints must not overwrite typed addresses.
        with QSignalBlocker(self.memory):
            self._refresh_memory_table()

    def _refresh_memory_table(self):
        self.previous_memory_button.setEnabled(self.cpu is not None and adjacent_page(self.inspected_address, -1) is not None)
        self.next_memory_button.setEnabled(self.cpu is not None and adjacent_page(self.inspected_address, 1) is not None)
        self.inspect_memory_button.setEnabled(self.cpu is not None)
        self.clear_memory_button.setEnabled(self.cpu is not None and self.inspected_address is not None)
        self.export_memory_button.setEnabled(self.cpu is not None)
        self.edit_memory_button.setEnabled(self.cpu is not None and not self.cpu.in_progress)
        if self.cpu is None:
            self.memory.setRowCount(0)
            self.memory_snapshot = ()
            return
        rows = memory_rows(self.cpu.memory, self.addresses, self.inspected_address)
        reshape, changed = refresh_plan(self.memory_snapshot, rows)
        selected_row = self.memory.currentRow()
        selected_column = self.memory.currentColumn()
        selected_address = (self.memory_snapshot[selected_row][0]
                            if 0 <= selected_row < len(self.memory_snapshot) else None)
        if reshape:
            self.memory.setRowCount(len(rows))
        for row in changed:
            address, word = rows[row]
            self.memory.setItem(row,0,QTableWidgetItem(f"{address:03X}"))
            self.memory.setItem(row,1,QTableWidgetItem(f"{word:04X}"))
            decoded = decode_word(word)
            item = QTableWidgetItem(decoded or self.t("Unsupported", "پشتیبانی‌نشده"))
            item.setToolTip(self.t("Interpretation only; a memory word may be data.", "فقط تفسیر؛ کلمه حافظه ممکن است داده باشد."))
            self.memory.setItem(row,2,item)
        self.memory_snapshot = tuple(rows)
        if reshape:
            selected = row_for_address(rows, selected_address)
            if selected is not None:
                self.memory.setCurrentCell(selected, max(0, selected_column))
            else:
                self.memory.setCurrentCell(-1, -1)
                self.memory.clearSelection()

    def inspect_memory(self):
        if self.cpu is None:
            self.status.setText(self.t("Assemble first.", "ابتدا اسمبل کنید."))
            return False
        try:
            address = parse_address(self.memory_address.text())
        except ValueError:
            self.status.setText(self.t("Enter 000–FFF.", "آدرس 000 تا FFF وارد کنید."))
            return False
        self.inspected_address = address
        page = page_addresses(address)
        self.memory_page_label.setText(f"{page[0]:03X}–{page[-1]:03X}")
        self.refresh_memory()
        for row in range(self.memory.rowCount()):
            if self.memory.item(row,0).text() == f"{address:03X}":
                self.memory.setCurrentCell(row,0)
                self.memory.scrollToItem(self.memory.item(row,0))
                break
        return True

    def edit_memory(self):
        self.pause()
        if self.cpu is None or self.history is None:
            self.status.setText(self.t("Assemble first.", "ابتدا اسمبل کنید."))
            return False
        if self.cpu.in_progress:
            self.status.setText(self.t("Finish or rewind current instruction first.",
                                      "ابتدا دستور جاری را کامل کنید یا به ابتدای آن بازگردید."))
            return False
        try:
            address = parse_address(self.memory_address.text())
        except ValueError:
            self.status.setText(self.t("Enter 000–FFF.", "آدرس 000 تا FFF وارد کنید."))
            return False
        old = self.cpu.memory[address]
        text, accepted = QInputDialog.getText(self, self.t("Edit memory word", "ویرایش کلمه حافظه"),
            self.t("New HEX word at ", "کلمه هگز جدید در آدرس ") + f"{address:03X} (0000–FFFF)",
            text=f"{old:04X}")
        if not accepted:
            return False
        try:
            word = parse_word(text)
        except ValueError:
            self.status.setText(self.t("Enter 0000–FFFF.", "کلمه 0000 تا FFFF وارد کنید."))
            return False
        if word == old:
            return False
        if QMessageBox.question(self, self.t("Change CPU memory?", "تغییر حافظه پردازنده؟"),
            f"M[{address:03X}]: {old:04X} → {word:04X}\n" +
            self.t("This starts a new reverse-history segment and may modify program instructions.",
                   "این کار بخش جدید تاریخچه بازگشت را آغاز می‌کند و ممکن است دستور برنامه را تغییر دهد."),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No) != QMessageBox.StandardButton.Yes:
            return False
        try:
            if not write_word(self.cpu, self.history, address, word):
                return False
        except ValueError as error:
            self.status.setText(error_text(error,self.fa))
            return False
        self.addresses.add(address)
        self.break_resume = None
        self.refresh()
        self.inspect_memory()
        self.status.setText(self.t("Memory updated; reverse history starts here.",
                                   "حافظه تغییر کرد؛ تاریخچه بازگشت از اینجا آغاز می‌شود."))
        return True

    def export_memory(self):
        if self.cpu is None:
            self.status.setText(self.t("Assemble first.", "ابتدا اسمبل کنید."))
            return False
        self.pause()
        name, _ = QFileDialog.getSaveFileName(self, self.t("Export visible memory", "خروجی حافظه نمایان"),
            "memory.csv", self.t("CSV files (*.csv)", "فایل CSV (*.csv)"))
        if not name:
            return False
        path = Path(name)
        if not path.suffix:
            path = path.with_suffix(".csv")
        try:
            memory_export.save(path, self.cpu.memory, self.addresses, self.inspected_address)
        except (OSError, ValueError):
            QMessageBox.warning(self, self.t("Export failed", "خروجی ناموفق"),
                self.t("Memory report could not be saved.", "گزارش حافظه ذخیره نشد."))
            return False
        self.status.setText(self.t("Memory report saved.", "گزارش حافظه ذخیره شد."))
        return True

    def clear_memory_page(self):
        self.reset_memory_page()
        self.refresh_memory()

    def step(self):
        if self.cpu is None:
            self.pause()
            return
        if self.steps >= 10000:
            self.pause()
            self.status.setText(self.t("Step limit reached. Reset to continue.","حد اجرای گام‌ها رسید؛ بازنشانی کنید."))
            return
        self.break_resume=None
        try:
            event = self.history.step()
        except ValueError as error:
            self.pause()
            self.status.setText(error_text(error,self.fa))
            return
        if event is None:
            self.pause()
            return
        self.steps = self.history.steps
        self.refresh(event)
        self.select_address(event.address)
        self.status.setText(f"{event.address:03X} · {event.mnemonic} · AC={self.cpu.ac:04X} · PC={self.cpu.pc:03X}")
        if self.cpu.halted:
            self.pause()

    def microstep(self):
        self.pause()
        if self.cpu is None or self.steps>=10000:return
        self.break_resume=None
        try:group=self.history.microstep()
        except ValueError as error:
            self.status.setText(error_text(error,self.fa));return
        if group is None:return
        self.steps=self.history.steps
        event=self.cpu.pending_event or self.cpu.completed_event
        self.refresh(event)
        self.select_address(event.address)
        self.cycles.groups.setCurrentCell(len(event.microevents)-1,0)
        self.status.setText(f"{event.mnemonic} · T{group.timing} · AC={self.cpu.ac:04X} · PC={self.cpu.pc:03X}")

    def microback(self):
        self.pause()
        if self.history is None:return
        group=self.history.microback()
        if group is None:return
        self.steps=self.history.steps
        self.break_resume=None
        pending=self.cpu.pending_event
        self.refresh(pending)
        self.select_address(pending.address if pending else self.cpu.pc)
        self.status.setText(self.t("Timing group reversed.","یک گروه زمانی واگرد شد."))

    def run(self):
        if self.cpu and not self.cpu.halted:
            self.timer.start(self.speed.value())

    def run_tick(self):
        if self.history and self.history.should_break() and self.break_resume != self.cpu.pc:
            self.break_resume=self.cpu.pc
            self.pause()
            self.status.setText(self.t("Breakpoint at ","توقف در ")+f"{self.cpu.pc:03X}")
            self.select_address(self.cpu.pc)
            return
        self.break_resume=None
        self.step()

    def pause(self):
        self.timer.stop()
        if hasattr(self, "datapath"):
            self.datapath.stop()

    def send_input(self):
        if self.cpu:
            try:
                self.pause()
                self.cpu.input_byte(int(self.input.text(),16))
                self.history.barrier()
                self.refresh()
            except ValueError as error:
                self.status.setText(error_text(error,self.fa))

    def read_output(self):
        if self.cpu:
            self.pause()
            try:byte = self.cpu.output_byte()
            except ValueError as error:
                self.status.setText(error_text(error,self.fa));return
            if byte is not None:self.history.barrier()
            self.refresh()
            self.status.setText(self.t("No output pending.","خروجی آماده نیست.") if byte is None else f"OUT: {byte:02X}")

    def back(self):
        self.pause()
        if self.history and self.history.back():
            self.steps=self.history.steps
            self.break_resume=None
            self.refresh()
            self.select_address(self.cpu.pc)
            self.status.setText(self.t("Reversed to PC=","بازگشت به PC=")+f"{self.cpu.pc:03X}")

    def toggle_breakpoint(self):
        if self.history is None:return
        try:
            address = parse_address(self.break_address.text())
        except ValueError:
            self.status.setText(self.t("Enter 000–FFF.","آدرس 000 تا FFF وارد کنید."))
            return
        self.history.toggle_breakpoint(address)
        self.break_resume=None
        self.refresh_trace()

    def trace_rows(self):
        if not self.history:return []
        return [(entry.number,f"{e.address:03X}",f"{e.word:04X}",e.mnemonic,
                 "—" if e.effective_address is None else f"{e.effective_address:03X}",
                 f"{e.after['AC']:04X}",f"{e.after['PC']:03X}")
                for entry in self.history.entries for e in (entry.event,)]

    def refresh_trace(self):
        partial=self.cpu.pending_event if self.cpu else None
        latest=partial or (self.history.entries[-1].event if self.history and self.history.entries else None)
        if self.cycles.current_trace != latest:self.cycles.show_event(latest,partial is not None)
        can_back=bool(self.history and (self.history.entries or self.cpu.in_progress))
        self.back_button.setEnabled(can_back)
        self.cycles.back_button.setEnabled(can_back)
        self.cycles.step_button.setEnabled(bool(self.cpu and not self.cpu.halted and self.steps<10000))
        rows=self.trace_rows()
        if rows!=self.visible_trace:
            # In the common forward-step case, insert only the new row.
            # At capacity, remove the oldest row before appending.
            previous=self.visible_trace
            if previous and len(rows)==len(previous) and rows[:-1]==previous[1:]:
                self.trace.removeRow(0)
                start=len(rows)-1
            elif rows[:len(previous)]==previous:
                start=len(previous)
            else:
                start=0
            self.trace.setRowCount(len(rows))
            for i in range(start,len(rows)):
                for j,value in enumerate(rows[i]):
                    self.trace.setItem(i,j,QTableWidgetItem(str(value)))
            self.visible_trace=rows
            if rows:self.trace.scrollToBottom()
        self.break_label.setText(self.t("Breakpoints: ","نقاط توقف: ")+
            (", ".join(f"{a:03X}" for a in sorted(self.history.breakpoints)) if self.history and self.history.breakpoints else "—"))

    def select_address(self,address):
        if not self.program or address not in self.program.source_lines:return
        block=self.source.document().findBlockByNumber(self.program.source_lines[address]-1)
        if block.isValid():
            self.source.setTextCursor(QTextCursor(block))
            self.source.ensureCursorVisible()

    def trace_selected(self,row,column):
        rows=self.trace_rows()
        if 0<=row<len(rows):
            self.select_address(int(rows[row][1],16))
            self.cycles.show_event(self.history.entries[row].event)

    def write_trace(self,path):
        with Path(path).open("w",encoding="utf-8-sig",newline="") as stream:
            writer=csv.writer(stream)
            writer.writerow(["Step","PC","Word","Mnemonic","EA","AC","Next PC"])
            writer.writerows(self.trace_rows())

    def export_trace(self):
        path,_=QFileDialog.getSaveFileName(self,self.t("Export trace","خروجی رد اجرا"),"trace.csv","CSV (*.csv)")
        if path:
            try:self.write_trace(Path(path) if Path(path).suffix else Path(path).with_suffix(".csv"))
            except OSError as exc:QMessageBox.warning(self,self.t("Export failed","خروجی ناموفق"),error_text(exc,self.fa))

    def use_registers(self):
        if self.cpu:self.arithmetic.set_operands(self.cpu.ac,self.cpu.dr,self.cpu.e)

    def done(self,result):
        if self.confirm_close():
            super().done(result)
