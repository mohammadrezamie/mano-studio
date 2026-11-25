"""Interactive Gray-ordered Karnaugh map using the exact minimizer."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QComboBox, QPushButton, QListWidget, QLineEdit)
from boolean_minimizer import gray_indices, minimize


class KarnaughView(QWidget):
    def __init__(self, fa=False):
        super().__init__()
        self.fa = fa
        self.values = [0]*16
        self.cells = {}
        box = QVBoxLayout(self)
        title = QLabel(self.t("Karnaugh map · exact minimization", "نقشه کارنو · ساده‌سازی دقیق"))
        title.setObjectName("brand")
        box.addWidget(title)
        hint = QLabel(self.t(
            "Activate a cell to cycle 0 → 1 → X → 0. X is a don't-care. Select a group to inspect its cells, including wrap-around.",
            "برای تغییر سلول بین ۰، ۱ و X آن را فعال کنید. X حالت بی‌تفاوت است. یک گروه را انتخاب کنید تا سلول‌های آن، شامل اتصال لبه‌ها، مشخص شوند."))
        hint.setWordWrap(True)
        box.addWidget(hint)
        controls = QHBoxLayout()
        controls.addWidget(QLabel(self.t("Variables", "متغیرها")))
        self.width = QComboBox()
        for n in (2,3,4):
            self.width.addItem(str(n),n)
        self.width.setCurrentIndex(2)
        self.width.setAccessibleName(self.t("Number of variables", "تعداد متغیرها"))
        controls.addWidget(self.width)
        self.form = QComboBox()
        self.form.addItem(self.t("SOP · group ones", "SOP · گروه‌بندی یک‌ها"),"SOP")
        self.form.addItem(self.t("POS · group zeros", "POS · گروه‌بندی صفرها"),"POS")
        self.form.setAccessibleName(self.t("Expression form", "نوع عبارت"))
        controls.addWidget(self.form,1)
        example = QPushButton(self.t("Example", "مثال"))
        example.clicked.connect(self.example)
        controls.addWidget(example)
        clear = QPushButton(self.t("Clear", "پاک کردن"))
        clear.clicked.connect(self.reset)
        controls.addWidget(clear)
        box.addLayout(controls)
        body = QHBoxLayout()
        self.map = QWidget()
        self.map.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.grid = QGridLayout(self.map)
        self.grid.setSpacing(8)
        body.addWidget(self.map,2)
        side = QVBoxLayout()
        side.addWidget(QLabel(self.t("Optimal groups", "گروه‌های بهینه")))
        self.groups = QListWidget()
        self.groups.setAccessibleName(self.t("Optimal groups; select to highlight", "گروه‌های بهینه؛ برای برجسته‌سازی انتخاب کنید"))
        self.groups.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        side.addWidget(self.groups,1)
        body.addLayout(side,1)
        box.addLayout(body,1)
        box.addWidget(QLabel(self.t("Simplified expression", "عبارت ساده‌شده")))
        self.expression = QLineEdit()
        self.expression.setReadOnly(True)
        self.expression.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.expression.setAccessibleName(self.t("Simplified expression", "عبارت ساده‌شده"))
        box.addWidget(self.expression)
        self.summary = QLabel()
        self.summary.setWordWrap(True)
        box.addWidget(self.summary)
        self.width.currentIndexChanged.connect(self.reset)
        self.form.currentIndexChanged.connect(self.refresh)
        self.groups.currentRowChanged.connect(self.highlight)
        self.example()

    def t(self,en,fa):
        return fa if self.fa else en

    def reset(self,*_):
        self.values = [0]*(2**self.width.currentData())
        self.rebuild()

    def example(self,*_):
        n = self.width.currentData()
        # A wrap-around cube in every supported size.
        self.values = [int(not (i & 1)) for i in range(2**n)]
        self.rebuild()

    def rebuild(self):
        while self.grid.count():
            item = self.grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.cells = {}
        n = self.width.currentData()
        matrix = gray_indices(n)
        cols = n - n//2
        self.grid.addWidget(QLabel("ABCD"[:n//2]+"/"+"ABCD"[n//2:n]),0,0)
        for c,index in enumerate(matrix[0]):
            self.grid.addWidget(QLabel(f"{index:0{cols}b}"),0,c+1)
        for r,row in enumerate(matrix):
            self.grid.addWidget(QLabel(f"{row[0]>>cols:0{n//2}b}"),r+1,0)
            for c,index in enumerate(row):
                button = QPushButton()
                button.setMinimumSize(66,64)
                button.setAutoDefault(False)
                button.clicked.connect(lambda checked=False,i=index:self.cycle(i))
                self.grid.addWidget(button,r+1,c+1)
                self.cells[index] = button
        self.refresh()

    def cycle(self,index):
        self.values[index] = {0:1,1:None,None:0}[self.values[index]]
        self.refresh()

    def refresh(self,*_):
        self.solution = minimize(self.values,self.form.currentData())
        self.expression.setText(self.solution.expression)
        self.groups.blockSignals(True)
        self.groups.clear()
        for i,group in enumerate(self.solution.groups,1):
            self.groups.addItem(f"G{i} · {group.pattern}  |  "+", ".join(map(str,group.cells)))
        self.groups.setCurrentRow(0 if self.solution.groups else -1)
        self.groups.blockSignals(False)
        count = len(self.solution.groups)
        literals = sum(g.literals for g in self.solution.groups)
        self.summary.setText(self.t(f"Groups: {count} · Literals: {literals}. Minimum groups, then minimum literals.",
                                    f"گروه‌ها: {count} · لیترال‌ها: {literals}. ابتدا کمترین گروه، سپس کمترین لیترال."))
        self.highlight(self.groups.currentRow())

    def highlight(self,row):
        active = self.solution.groups[row].cells if 0 <= row < len(self.solution.groups) else ()
        for i,button in self.cells.items():
            value = "X" if self.values[i] is None else str(self.values[i])
            membership = [f"G{j}" for j,g in enumerate(self.solution.groups,1) if i in g.cells]
            marker = "▶ " if i in active else ""
            button.setText(f"{marker}{value}\nm{i}"+("\n"+" ".join(membership) if membership else ""))
            button.setAccessibleName(self.t(f"Minterm {i}, value {value}",f"مین‌ترم {i}، مقدار {value}")+
                                     (" · "+", ".join(membership) if membership else ""))
            button.setProperty("groupSelected",i in active)
            button.setStyleSheet("border: 2px solid palette(highlight);" if i in active else "")
