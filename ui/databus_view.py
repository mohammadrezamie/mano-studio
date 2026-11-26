"""Interactive shared-bus lab with reproducible stepwise experiments."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QWidget,QVBoxLayout,QHBoxLayout,QGridLayout,QLabel,
    QCheckBox,QSpinBox,QPushButton,QComboBox,QTableWidget,QTableWidgetItem,
    QHeaderView,QAbstractItemView,QMessageBox,QFileDialog)
from databus_lab import Databus,SOURCES,DESTINATIONS,event_controls
from word_arithmetic import OPERATIONS
from databus_samples import SAMPLES,sample
import databus_file
from pathlib import Path


class DatabusView(QWidget):
    def __init__(self,fa=False):
        super().__init__()
        self.fa=fa
        self.model=Databus()
        self.scenario=None
        self.step_index=0
        layout=QVBoxLayout(self)
        note=QLabel(self.t("One ideal 4-bit bus connects AR, R0, R1, ALU and RAM (16 × 4). A clock edge samples the old source and old AR. Select one driver when loading destinations.",
            "یک گذرگاه ایده‌آل ۴ بیتی، AR، R0، R1، ALU و RAM (۱۶ × ۴) را متصل می‌کند. لبه ساعت از مبدأ و AR قبلی نمونه می‌گیرد. هنگام بارگذاری فقط یک راه‌انداز انتخاب کنید."))
        note.setWordWrap(True)
        layout.addWidget(note)
        row=QHBoxLayout()
        self.examples=QComboBox()
        for s in SAMPLES:
            self.examples.addItem(s["title"][fa],s["id"])
        self.examples.setAccessibleName(self.t("Saved experiments","آزمایش‌های ذخیره‌شده"))
        row.addWidget(self.examples,1)
        for en,fa_text,fn in (("Load example","بارگذاری نمونه",self.load_example),("Next example step","گام بعد نمونه",self.next_step),("Reset","بازنشانی",self.reset)):
            button=QPushButton(self.t(en,fa_text))
            button.clicked.connect(fn)
            row.addWidget(button)
            if en=="Next example step":
                self.next_button=button
        layout.addLayout(row)
        files=QHBoxLayout()
        for en,fa_text,fn in (("Open experiment","باز کردن آزمایش",self.open_file),
                               ("Save experiment","ذخیره آزمایش",self.save_file)):
            button=QPushButton(self.t(en,fa_text))
            button.clicked.connect(fn)
            files.addWidget(button)
        files.addStretch()
        layout.addLayout(files)
        self.task=QLabel()
        self.task.setWordWrap(True)
        layout.addWidget(self.task)
        grid=QGridLayout()
        self.drivers={}
        self.loads={}
        self.words={}
        for col,heading in enumerate((self.t("Device","قطعه"),self.t("Value","مقدار"),self.t("Drive bus","راه‌اندازی"),self.t("Load at edge","بارگذاری در لبه"))):
            grid.addWidget(QLabel(heading),0,col)
        for i,name in enumerate(SOURCES,1):
            grid.addWidget(QLabel(name),i,0)
            if name=="EXT":
                self.external=QSpinBox()
                self.external.setRange(0,15)
                self.external.setDisplayIntegerBase(16)
                self.external.setAccessibleName(self.t("External data word","کلمه داده خارجی"))
                self.external.valueChanged.connect(self.refresh)
                grid.addWidget(self.external,i,1)
            else:
                self.words[name]=QLabel()
                self.words[name].setLayoutDirection(Qt.LayoutDirection.LeftToRight)
                grid.addWidget(self.words[name],i,1)
            check=QCheckBox()
            check.setAccessibleName(self.t("Drive bus from ","راه‌اندازی گذرگاه از ")+name)
            self.drivers[name]=check
            check.toggled.connect(self.refresh)
            grid.addWidget(check,i,2)
            if name in DESTINATIONS:
                check=QCheckBox()
                check.setAccessibleName(self.t("Load ","بارگذاری ")+name)
                self.loads[name]=check
                check.toggled.connect(self.refresh)
                grid.addWidget(check,i,3)
        layout.addLayout(grid)
        alu_row=QHBoxLayout()
        alu_row.addWidget(QLabel(self.t("ALU: R0, R1","واحد حساب و منطق: R0، R1")))
        self.operation=QComboBox()
        self.operation.addItems(OPERATIONS)
        self.operation.setAccessibleName(self.t("ALU operation","عملیات واحد حساب و منطق"))
        alu_row.addWidget(self.operation)
        self.carry=QCheckBox("Cin")
        alu_row.addWidget(self.carry)
        self.flags=QLabel()
        self.flags.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        alu_row.addWidget(self.flags,1)
        layout.addLayout(alu_row)
        self.operation.currentIndexChanged.connect(self.refresh)
        self.carry.toggled.connect(self.refresh)
        row=QHBoxLayout()
        self.bus=QLabel()
        self.bus.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        row.addWidget(self.bus,1)
        pulse=QPushButton(self.t("Clock edge","لبه ساعت"))
        pulse.setObjectName("primary")
        pulse.clicked.connect(self.tick)
        row.addWidget(pulse)
        layout.addLayout(row)
        self.status=QLabel()
        self.status.setWordWrap(True)
        layout.addWidget(self.status)
        self.memory=QTableWidget(4,4)
        self.memory.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.memory.setHorizontalHeaderLabels(["+0","+1","+2","+3"])
        self.memory.setVerticalHeaderLabels(["0","4","8","C"])
        self.memory.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.memory.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        layout.addWidget(self.memory,1)
        self.trace=QTableWidget(0,5)
        self.trace.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.trace.setHorizontalHeaderLabels([self.t("Old AR,R0,R1","مقادیر قبلی"),"BUS",self.t("New AR,R0,R1","مقادیر جدید"),self.t("RAM write","نوشتن RAM"),self.t("ALU C/V/N/Z","پرچم‌های ALU")])
        self.trace.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.trace.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.trace.verticalHeader().hide()
        layout.addWidget(self.trace,1)
        self.refresh()
        self.update_task()
        self.saved_checkpoint=databus_file.snapshot(self.model,self.controls())

    def t(self,en,fa):
        return fa if self.fa else en

    def controls(self):
        return event_controls(tuple(n for n,c in self.drivers.items() if c.isChecked()),
                tuple(n for n,c in self.loads.items() if c.isChecked()),self.external.value(),
                self.operation.currentText(),int(self.carry.isChecked()))

    @staticmethod
    def flag_text(result):
        if result is None:
            return "—"
        bit=lambda value: "—" if value is None else str(int(value))
        return " / ".join(bit(v) for v in (result.carry,result.overflow,result.negative,result.zero))

    def refresh(self,*_):
        arithmetic=self.model.arithmetic(self.operation.currentText(),int(self.carry.isChecked()))
        for name,widget in self.words.items():
            word=arithmetic.word if name=="ALU" else self.model.memory.read(self.model.registers["AR"]) if name=="RAM" else self.model.registers[name]
            widget.setText(f"{word:X}")
        self.flags.setText("C / V / N / Z = "+self.flag_text(arithmetic))
        sources,destinations,external,*alu_controls=self.controls()
        bus=self.model.preview(sources,external,*alu_controls)
        self.bus.setText("BUS[3:0] = "+bus.bits)
        self.status.setText(self.t("Transfer ready","انتقال آماده") if bus.drivers==1 else
            self.t("No driver / Z","بدون راه‌انداز / Z") if not bus.drivers else
            self.t("Multiple drivers; load is blocked","چند راه‌انداز؛ بارگذاری مسدود است"))
        for a in range(16):
            item=QTableWidgetItem(f"{self.model.memory.read(a):X}")
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.memory.setItem(a//4,a%4,item)
        self.trace.setRowCount(len(self.model.history))
        for i,cycle in enumerate(self.model.history):
            write="—" if cycle.memory_write is None else f"M[{cycle.memory_write[0]:X}] ← {cycle.memory_write[2]:X}"
            for j,value in enumerate((" ".join(f"{v:X}" for v in cycle.before),cycle.bus,
                                       " ".join(f"{v:X}" for v in cycle.after),write,self.flag_text(cycle.arithmetic))):
                self.trace.setItem(i,j,QTableWidgetItem(value))
        self.trace.scrollToBottom()

    def apply_cycle(self):
        try:
            self.model.tick(*self.controls())
        except ValueError:
            self.status.setText(self.t("Transfer rejected; registers and RAM unchanged.",
                "انتقال رد شد؛ ثبات‌ها و RAM بدون تغییر ماندند."))
            return False
        self.refresh()
        return True

    def tick(self):
        if self.apply_cycle():
            # Manual work is independent of scripted replay.
            self.scenario=None
            self.update_task()

    def reset_state(self):
        self.model.reset()
        for control in (*self.drivers.values(),*self.loads.values()):
            control.setChecked(False)
        self.external.setValue(0)
        self.operation.setCurrentText("ADD")
        self.carry.setChecked(False)
        self.refresh()
        self.saved_checkpoint=databus_file.snapshot(self.model,self.controls())

    def install_checkpoint(self,model,staged):
        self.model=model
        self.scenario=None
        self.step_index=0
        sources,destinations,external,*alu_controls=staged
        operation,carry=alu_controls or ("ADD",0)
        self.operation.setCurrentText(operation)
        self.carry.setChecked(bool(carry))
        for name,control in self.drivers.items():
            control.blockSignals(True)
            control.setChecked(name in sources)
            control.blockSignals(False)
        for name,control in self.loads.items():
            control.blockSignals(True)
            control.setChecked(name in destinations)
            control.blockSignals(False)
        self.external.blockSignals(True)
        self.external.setValue(external)
        self.external.blockSignals(False)
        self.refresh()
        self.update_task()
        self.saved_checkpoint=databus_file.snapshot(self.model,self.controls())

    def open_file(self):
        name,_=QFileDialog.getOpenFileName(self,self.t("Open experiment","باز کردن آزمایش"),"",
            "Mano Studio (*.mano)")
        if not name:
            return
        try:
            model,staged=databus_file.load(name)
        except (OSError,UnicodeError,ValueError):
            QMessageBox.warning(self,self.t("Invalid experiment","آزمایش نامعتبر"),
                self.t("Cannot open this bus experiment.","این آزمایش گذرگاه باز نمی‌شود."))
            return
        if self.confirm_reset():
            self.install_checkpoint(model,staged)

    def save_file(self):
        name,_=QFileDialog.getSaveFileName(self,self.t("Save experiment","ذخیره آزمایش"),
            "bus-experiment.mano","Mano Studio (*.mano)")
        if not name:
            return False
        path=Path(name)
        if path.suffix.lower()!=".mano":
            path=Path(str(path)+".mano")
        try:
            databus_file.save(path,self.model,self.controls())
        except (OSError,UnicodeError,ValueError):
            QMessageBox.warning(self,self.t("Cannot save","ذخیره ناموفق"),
                self.t("The experiment could not be saved.","آزمایش ذخیره نشد."))
            return False
        self.saved_checkpoint=databus_file.snapshot(self.model,self.controls())
        self.status.setText(self.t("Experiment saved.","آزمایش ذخیره شد."))
        return True

    def confirm_reset(self):
        return not self.is_dirty() or QMessageBox.question(self,self.t("Reset experiment","بازنشانی آزمایش"),
            self.t("Discard the current bus experiment and reset RAM/registers?","آزمایش فعلی کنار گذاشته و RAM و ثبات‌ها بازنشانی شوند؟"))==QMessageBox.StandardButton.Yes

    def is_dirty(self):
        return databus_file.snapshot(self.model,self.controls())!=self.saved_checkpoint

    def confirm_close(self):
        if not self.is_dirty():
            return True
        choice=QMessageBox.question(self,self.t("Unsaved experiment","آزمایش ذخیره‌نشده"),
            self.t("Save your bus experiment before closing?","آزمایش گذرگاه پیش از بستن ذخیره شود؟"),
            QMessageBox.StandardButton.Save|QMessageBox.StandardButton.Discard|QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Save)
        if choice==QMessageBox.StandardButton.Save:
            return self.save_file()
        return choice==QMessageBox.StandardButton.Discard

    def reset(self):
        if self.confirm_reset():
            self.scenario=None
            self.reset_state()
            self.update_task()

    def load_example(self):
        if self.confirm_reset():
            self.reset_state()
            self.scenario=sample(self.examples.currentData())
            self.step_index=0
            self.update_task()

    def update_task(self):
        active=self.scenario is not None
        self.next_button.setEnabled(active and self.step_index<len(self.scenario["steps"]))
        if not active:
            self.task.setText(self.t("Choose an example or perform your own transfers.","نمونه‌ای انتخاب کنید یا انتقال‌های دلخواه را انجام دهید."))
        else:
            self.task.setText(self.scenario["task"][self.fa]+f" · {self.step_index}/{len(self.scenario['steps'])}")

    def next_step(self):
        if self.scenario is None or self.step_index>=len(self.scenario["steps"]):
            return
        step=self.scenario["steps"][self.step_index]
        for name,control in self.drivers.items():
            control.setChecked(name in step["sources"])
        for name,control in self.loads.items():
            control.setChecked(name in step["destinations"])
        self.external.setValue(step["external"])
        self.operation.setCurrentText(step.get("operation","ADD"))
        self.carry.setChecked(bool(step.get("carry",0)))
        if self.apply_cycle():
            self.step_index+=1
            self.update_task()
