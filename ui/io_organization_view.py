"""Bilingual Chapter 11 asynchronous I/O and priority inspector."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QWidget,QVBoxLayout,QHBoxLayout,QLabel,QComboBox,QSpinBox,QCheckBox,
    QPushButton,QTableWidget,QTableWidgetItem,QHeaderView,QAbstractItemView,QTabWidget)
from io_organization import Handshake,PriorityInterrupt


class IOOrganizationView(QWidget):
    def __init__(self,fa=False):
        super().__init__()
        self.fa=fa
        layout=QVBoxLayout(self)
        self.tabs=QTabWidget();layout.addWidget(self.tabs)
        self.tabs.addTab(self.handshake_page(),self.t("Handshake","دست‌دهی"))
        self.tabs.addTab(self.interrupt_page(),self.t("Priority interrupt","وقفه اولویت‌دار"))

    def t(self,en,fa):return fa if self.fa else en

    def table(self,headers):
        table=QTableWidget(0,len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        return table

    def handshake_page(self):
        page=QWidget();layout=QVBoxLayout(page)
        note=QLabel(self.t("Asynchronous events, not fixed clock cycles. Source drives DATA and VALID; destination drives READY (data accepted in source-initiated mode). The bus is stable while valid.",
            "رویدادهای ناهمگام، نه چرخه ساعت ثابت. مبدأ DATA و VALID و مقصد READY (پذیرش داده در حالت شروع از مبدأ) را کنترل می‌کند. داده هنگام VALID ثابت می‌ماند."))
        note.setWordWrap(True);layout.addWidget(note)
        row=QHBoxLayout()
        self.handshake_mode=QComboBox()
        self.handshake_mode.addItem(self.t("Source initiated","شروع از مبدأ"),"source")
        self.handshake_mode.addItem(self.t("Destination initiated","شروع از مقصد"),"destination")
        row.addWidget(self.handshake_mode)
        self.byte=QSpinBox();self.byte.setRange(0,255);self.byte.setDisplayIntegerBase(16);self.byte.setValue(0x41)
        row.addWidget(QLabel("DATA HEX"));row.addWidget(self.byte)
        reset=QPushButton(self.t("Reset","بازنشانی"));reset.clicked.connect(self.reset_handshake);row.addWidget(reset)
        layout.addLayout(row)
        row=QHBoxLayout();self.actions={}
        for action,en,fa_label in (("offer","Offer","عرضه"),("accept","Accept","پذیرش"),("request","Request","درخواست"),
                ("provide","Provide","ارائه"),("receive","Receive","دریافت"),("release_data","Release data","آزادسازی داده"),("release_ready","Release ready","آزادسازی آمادگی")):
            button=QPushButton(self.t(en,fa_label))
            button.clicked.connect(lambda _checked=False,a=action:self.advance(a))
            self.actions[action]=button;row.addWidget(button)
        layout.addLayout(row)
        self.handshake_state=QLabel();self.handshake_state.setWordWrap(True);layout.addWidget(self.handshake_state)
        self.handshake_trace=self.table(["#",self.t("Event","رویداد"),"VALID","READY","DATA",self.t("Captured","دریافت")])
        layout.addWidget(self.handshake_trace,1)
        self.handshake_mode.currentIndexChanged.connect(self.reset_handshake)
        self.reset_handshake()
        return page

    def reset_handshake(self,*_):
        self.handshake=Handshake(self.handshake_mode.currentData())
        self.handshake_trace.setRowCount(0)
        self.refresh_handshake()

    def refresh_handshake(self):
        h=self.handshake
        for action,button in self.actions.items():
            button.setVisible(action in h.SEQUENCES[h.mode])
            button.setEnabled(action==h.next_action)
        self.byte.setEnabled(h.next_action in ("offer","provide"))
        bus="—" if h.bus is None else f"{h.bus:02X}"
        self.handshake_state.setText(f"VALID={int(h.valid)} | READY={int(h.ready)} | DATA={bus} | "+self.t("Received","دریافت‌شده")+f": {len(h.received)}")

    def advance(self,action):
        if action!=self.handshake.next_action:return
        event=self.handshake.act(action,self.byte.value() if action in ("offer","provide") else None)
        row=self.handshake_trace.rowCount()
        self.handshake_trace.insertRow(row)
        values=(event.number,self.actions[action].text(),int(event.valid),int(event.ready),
                "—" if event.bus is None else f"{event.bus:02X}",
                "—" if event.received is None else f"{event.received:02X}")
        for col,value in enumerate(values):self.handshake_trace.setItem(row,col,QTableWidgetItem(str(value)))
        self.handshake_trace.scrollToBottom();self.refresh_handshake()

    def interrupt_page(self):
        page=QWidget();layout=QVBoxLayout(page)
        note=QLabel(self.t("IRQ0 highest; mask bit 1 enables. Acknowledge clears selected pending bit; only higher priorities can nest. EOI returns from current service. Vector addresses are illustrative.",
            "IRQ0 بالاترین اولویت؛ بیت ماسک ۱ به معنای فعال است. تأیید، بیت انتظار انتخابی را پاک می‌کند؛ فقط اولویت بالاتر می‌تواند تو در تو شود. EOI پایان سرویس جاری است. آدرس بردارها نمونه آموزشی‌اند."))
        note.setWordWrap(True);layout.addWidget(note)
        row=QHBoxLayout()
        for i in range(4):
            b=QPushButton(f"IRQ{i}");b.clicked.connect(lambda _checked=False,d=i:self.request(d));row.addWidget(b)
        self.mask=QSpinBox();self.mask.setRange(0,15);self.mask.setDisplayIntegerBase(2);self.mask.setValue(15)
        row.addWidget(QLabel("MASK"));row.addWidget(self.mask)
        self.enable=QCheckBox("IEN");self.enable.setChecked(True);row.addWidget(self.enable)
        layout.addLayout(row)
        row=QHBoxLayout()
        self.ack=QPushButton(self.t("Acknowledge","تأیید وقفه"));self.ack.clicked.connect(self.acknowledge);row.addWidget(self.ack)
        self.eoi=QPushButton("EOI");self.eoi.clicked.connect(self.end);row.addWidget(self.eoi)
        reset=QPushButton(self.t("Reset","بازنشانی"));reset.clicked.connect(self.reset_interrupt);row.addWidget(reset)
        layout.addLayout(row)
        self.irq_state=QLabel();self.irq_state.setWordWrap(True);layout.addWidget(self.irq_state)
        self.irq_table=self.table(["IRQ",self.t("Pending","انتظار"),self.t("Mask","ماسک"),self.t("Eligible","مجاز"),"PI","ACK","PO"])
        layout.addWidget(self.irq_table,1)
        self.irq_status=QLabel();self.irq_status.setWordWrap(True);layout.addWidget(self.irq_status)
        self.irq=PriorityInterrupt()
        self.mask.valueChanged.connect(self.configure_irq);self.enable.toggled.connect(self.configure_irq)
        self.refresh_irq()
        return page

    def reset_interrupt(self):
        self.irq=PriorityInterrupt()
        self.mask.setValue(15);self.enable.setChecked(True)
        self.irq_status.clear();self.refresh_irq()

    def configure_irq(self,*_):
        self.irq.set_mask(self.mask.value())
        self.irq.enabled=self.enable.isChecked()
        self.irq_status.clear();self.refresh_irq()

    def request(self,device):
        self.irq.request(device)
        self.irq_status.setText(f"IRQ{device}")
        self.refresh_irq()

    def refresh_irq(self):
        s=self.irq.select()
        winner="—" if s.winner is None else f"IRQ{s.winner} → {s.vector:04X}"
        service=" → ".join(f"IRQ{i}" for i in self.irq.service) or "—"
        self.irq_state.setText(f"IR={s.pending:04b} | MASK={s.mask:04b} | "+self.t("Selected","انتخاب‌شده")+f": {winner} | "+self.t("Service stack","پشته سرویس")+f": {service}")
        self.irq_table.setRowCount(4)
        for i,pi,accepted,po in s.grant:
            values=(i,(s.pending>>i)&1,(s.mask>>i)&1,(s.eligible>>i)&1,int(pi),int(accepted),int(po))
            for col,value in enumerate(values):self.irq_table.setItem(i,col,QTableWidgetItem(str(value)))
        self.ack.setEnabled(s.winner is not None);self.eoi.setEnabled(bool(self.irq.service))

    def acknowledge(self):
        if self.irq.select().winner is None:return
        s=self.irq.acknowledge()
        self.irq_status.setText(f"ACK IRQ{s.winner} → {s.vector:04X}")
        self.refresh_irq()

    def end(self):
        if not self.irq.service:return
        self.irq_status.setText(f"EOI IRQ{self.irq.end()}")
        self.refresh_irq()
