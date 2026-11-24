"""Integrated fixed-width representation and ALU workbench."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QWidget,QVBoxLayout,QHBoxLayout,QLabel,QComboBox,QLineEdit,
    QCheckBox,QTableWidget,QTableWidgetItem,QHeaderView,QAbstractItemView)
from word_arithmetic import WIDTHS,OPERATIONS,alu,parse_word,representations
from arithmetic_algorithms import booth, restoring_division, nonrestoring_division, signed_division

class ArithmeticView(QWidget):
    def __init__(self,fa=False):
        super().__init__()
        self.fa=fa
        self.result=None
        layout=QVBoxLayout(self)
        row=QHBoxLayout()
        row.addWidget(QLabel(self.t("Word width","طول کلمه")))
        self.width=QComboBox()
        for n in WIDTHS:self.width.addItem(f"{n} "+self.t("bit","بیت"),n)
        self.width.setCurrentIndex(self.width.findData(16))
        row.addWidget(self.width)
        row.addWidget(QLabel(self.t("Input base","مبنای ورودی")))
        self.base=QComboBox()
        for name,n in [("BIN",2),("OCT",8),("DEC",10),("HEX",16)]:self.base.addItem(name,n)
        self.base.setCurrentIndex(3)
        self.previous_base=16
        row.addWidget(self.base)
        self.op=QComboBox()
        self.op.addItems(OPERATIONS)
        self.op.insertItem(0,self.t("Convert bases","تبدیل مبنا"),"convert")
        self.op.addItem(self.t("Booth signed multiply","ضرب علامت‌دار بوث"),"booth")
        self.op.addItem(self.t("Restoring unsigned divide","تقسیم بدون علامت بازگرداننده"),"divide")
        self.op.addItem(self.t("Non-restoring unsigned divide","تقسیم بدون علامت غیربازگرداننده"),"nonrestore")
        self.op.addItem(self.t("Restoring signed divide","تقسیم علامت‌دار بازگرداننده"),"signeddivide")
        self.op.setCurrentIndex(1)
        row.addWidget(self.op,1)
        self.cin=QCheckBox("Cin / E")
        row.addWidget(self.cin)
        layout.addLayout(row)
        row=QHBoxLayout()
        self.a=QLineEdit("7FFF")
        self.b=QLineEdit("0001")
        for name,edit in [("A",self.a),("B",self.b)]:
            row.addWidget(QLabel(name))
            edit.setMaxLength(32)
            edit.setAccessibleName(name)
            edit.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
            row.addWidget(edit,1)
        layout.addLayout(row)
        self.representation=QTableWidget(3,6)
        self.representation.setHorizontalHeaderLabels([self.t("Word","کلمه"),"BIN","OCT","HEX",self.t("Unsigned","بدون علامت"),self.t("Signed","علامت‌دار")])
        self.representation.verticalHeader().hide()
        self.representation.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.representation.horizontalHeader().setStretchLastSection(True)
        self.representation.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.representation.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.representation.setMaximumHeight(132)
        layout.addWidget(self.representation)
        self.flags=QLabel()
        self.flags.setObjectName("section")
        self.flags.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        layout.addWidget(self.flags)
        self.note=QLabel(self.t("C: carry (SUB: no borrow). V: signed overflow. N: sign. Z: zero. Teaching flags are not extra Mano CPU registers.",
             "C: نقلی (در تفریق: بدون قرض). V: سرریز علامت‌دار. N: علامت. Z: صفر. این پرچم‌های آموزشی ثبات‌های اضافی مانو نیستند."))
        self.note.setWordWrap(True)
        layout.addWidget(self.note)
        self.stages=QTableWidget(0,6)
        self.stages.setHorizontalHeaderLabels([self.t("Bit","بیت"),"A","B′ / B","Cin",self.t("Sum","جمع"),"Cout"])
        self.stages.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.stages.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.stages.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        layout.addWidget(self.stages,1)
        self.status=QLabel()
        self.status.setWordWrap(True)
        self.status.setProperty("state","error")
        layout.addWidget(self.status)
        for control in (self.width,self.op):
            control.currentIndexChanged.connect(self.refresh)
        self.base.currentIndexChanged.connect(self.change_base)
        self.cin.toggled.connect(self.refresh)
        self.a.textChanged.connect(self.refresh)
        self.b.textChanged.connect(self.refresh)
        self.refresh()

    def t(self,en,fa):
        return fa if self.fa else en

    def change_base(self,*_):
        new=self.base.currentData()
        width=self.width.currentData()
        keys={2:"BIN",8:"OCT",10:"Unsigned",16:"HEX"}
        for edit in (self.a,self.b):
            try:
                word=parse_word(edit.text(),self.previous_base,width)
            except ValueError:
                continue
            edit.blockSignals(True)
            edit.setText(representations(word,width)[keys[new]])
            edit.blockSignals(False)
        self.previous_base=new
        self.refresh()

    def set_operands(self,a,b,e=0):
        for edit in (self.a,self.b):edit.blockSignals(True)
        self.width.setCurrentIndex(self.width.findData(16))
        self.base.blockSignals(True)
        self.base.setCurrentIndex(self.base.findData(16))
        self.previous_base=16
        self.base.blockSignals(False)
        self.a.setText(f"{a:04X}")
        self.b.setText(f"{b:04X}")
        self.cin.setChecked(bool(e))
        for edit in (self.a,self.b):edit.blockSignals(False)
        self.refresh()

    def refresh(self,*_):
        width=self.width.currentData()
        base=self.base.currentData()
        mode=self.op.currentData()
        op="CONVERT" if mode=="convert" else self.op.currentText()
        if mode in ("booth","divide","nonrestore","signeddivide"):
            self.refresh_algorithm(mode,width,base)
            return
        self.note.setText(self.t("C: carry (SUB: no borrow). V: signed overflow. N: sign. Z: zero. Teaching flags are not extra Mano CPU registers.", "C: نقلی (در تفریق: بدون قرض). V: سرریز علامت‌دار. N: علامت. Z: صفر. این پرچم‌های آموزشی ثبات‌های اضافی مانو نیستند."))
        self.stages.setColumnCount(6)
        self.stages.setHorizontalHeaderLabels([self.t("Bit","بیت"),"A","B′ / B","Cin",self.t("Sum","جمع"),"Cout"])
        binary=op in ("ADD","ADC","SUB","AND","OR","XOR")
        conversion=op=="CONVERT"
        self.note.setVisible(not conversion)
        self.stages.setVisible(not conversion)
        self.representation.setRowCount(1 if conversion else 3)
        self.b.setEnabled(binary)
        self.cin.setEnabled(op in ("ADC","CIR","CIL"))
        self.representation.clearContents()
        self.stages.setRowCount(0)
        self.flags.clear()
        self.result=None
        try:
            a=parse_word(self.a.text(),base,width)
            b=parse_word(self.b.text(),base,width) if binary else 0
            result=None if op=="CONVERT" else alu(op,a,b,width,int(self.cin.isChecked()))
        except ValueError as exc:
            self.status.setText(self.t(str(exc),"عدد ورودی یا طول کلمه معتبر نیست."))
            return
        self.status.clear()
        self.result=result
        words=(("A",a),) if conversion else (("A",a),("B",b if binary else None),(self.t("Result","نتیجه"),result.word))
        for row,(label,word) in enumerate(words):
            values=[label]+(list(representations(word,width).values()) if word is not None else ["—"]*5)
            for col,value in enumerate(values):
                item=QTableWidgetItem(value)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.representation.setItem(row,col,item)
        if result is None:
            self.flags.setText(self.t("Same word in all four bases","همان کلمه در چهار مبنا"))
            return
        def flag(v):return "—" if v is None else str(int(v))
        self.flags.setText(f"C = {flag(result.carry)}    V = {flag(result.overflow)}    N = {flag(result.negative)}    Z = {flag(result.zero)}")
        self.stages.setRowCount(len(result.stages))
        for row,stage in enumerate(result.stages):
            for col,value in enumerate(stage):
                item=QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.stages.setItem(row,col,item)

    def refresh_algorithm(self,mode,width,base):
        """Reuse the existing operand controls, word table and trace table."""
        self.result=None
        self.b.setEnabled(True)
        self.cin.setEnabled(False)
        self.note.show()
        self.stages.show()
        self.representation.setRowCount(2)
        self.representation.clearContents()
        self.stages.setRowCount(0)
        self.flags.clear()
        is_booth=mode=="booth"
        if is_booth:
            self.note.setText(self.t(
                "Signed two's complement. Q0 Q−1: 01 adds M, 10 subtracts M; then arithmetic right shift. A is n+1 bits (shown signed). Product is 2n bits.",
                "متمم دو علامت‌دار. زوج ۰۱ موجب جمع و ۱۰ موجب تفریق M است؛ سپس شیفت حسابی راست. A با n+1 بیت به‌صورت علامت‌دار و حاصل با 2n بیت نمایش داده می‌شود."))
            headers=[self.t("Cycle","چرخه"),"Q0 Q−1",self.t("Action","عمل"),"A "+self.t("before shift","پیش از شیفت"),"A","Q","Q−1"]
        elif mode=="nonrestore":
            self.note.setText(self.t(
                "Unsigned non-restoring division: old R sign selects −B or +B after shift; new R sign selects quotient bit. Add B once if final R is negative.",
                "تقسیم غیربازگرداننده: علامت قبلی R تعیین‌کننده جمع یا تفریق B پس از شیفت است؛ علامت جدید R بیت خارج‌قسمت را تعیین می‌کند. اگر R نهایی منفی باشد، یک بار B اضافه می‌شود."))
            headers=[self.t("Cycle","چرخه"),"2R + bit",self.t("Action","عمل"),"R", "Q"]
        elif mode=="signeddivide":
            self.note.setText(self.t(
                "Two's complement inputs; divide |A| by |B|, then set quotient sign and remainder sign. Truncate toward zero. Trace shows unsigned magnitudes.",
                "ورودی متمم دو؛ قدر مطلق A بر قدر مطلق B تقسیم می‌شود، سپس علامت خارج‌قسمت و باقی‌مانده اعمال می‌شود. گرد کردن به سمت صفر است؛ جدول قدر مطلق‌ها را نشان می‌دهد."))
            headers=[self.t("Cycle","چرخه"),"R "+self.t("shifted","شیفت‌یافته"),"R − |B|",self.t("Restore?","بازگردانی؟"),"R","Q"]
        else:
            self.note.setText(self.t(
                "Unsigned division. Shift (R,Q), subtract divisor, restore R if negative; append quotient bit. R < divisor after each cycle.",
                "تقسیم بدون علامت. ابتدا (R,Q) شیفت داده می‌شود؛ مقسوم‌علیه کم می‌شود و در صورت منفی شدن R بازگردانی می‌شود؛ سپس بیت خارج‌قسمت تعیین می‌شود."))
            headers=[self.t("Cycle","چرخه"),"R "+self.t("shifted","شیفت‌یافته"),"R − B",self.t("Restore?","بازگردانی؟"),"R","Q"]
        self.stages.setColumnCount(len(headers))
        self.stages.setHorizontalHeaderLabels(headers)
        try:
            a=parse_word(self.a.text(),base,width)
            b=parse_word(self.b.text(),base,width)
            if is_booth:
                product,trace=booth(a,b,width)
                self.flags.setText(f"{self.t('Product','حاصل‌ضرب')} = {product}   |   {product & ((1 << (2*width))-1):0{2*width}b}")
                rows=[(r.cycle,r.pair,r.operation,r.accumulator_after_operation,r.accumulator,f"{r.multiplier:0{width}b}",r.previous_bit) for r in trace]
            else:
                if mode!="signeddivide" and base==10 and (int(self.a.text())<0 or int(self.b.text())<0):
                    raise ValueError("Unsigned operands required")
                if b==0:
                    self.status.setText(self.t("Division by zero","تقسیم بر صفر مجاز نیست."))
                    return
                suffix=""
                if mode=="nonrestore":
                    answer=nonrestoring_division(a,b,width)
                    q,r,trace=answer.quotient,answer.remainder,answer.steps
                    rows=[(s.cycle,s.shifted_remainder,s.operation,s.partial_remainder,f"{s.quotient:0{width}b}") for s in trace]
                    if answer.correction:
                        rows.append((self.t("Final","نهایی"),"—","+B",r,f"{q:0{width}b}"))
                else:
                    if mode=="signeddivide":
                        answer=signed_division(a,b,width)
                        q,r,trace=answer.quotient,answer.remainder,answer.steps
                        suffix=f" | |A| = {answer.magnitude_dividend}, |B| = {answer.magnitude_divisor}"
                        if answer.overflow:
                            suffix+=" | "+self.t("Signed quotient overflow","سرریز خارج‌قسمت علامت‌دار")
                    else:
                        q,r,trace=restoring_division(a,b,width)
                    rows=[(s.cycle,s.shifted_remainder,s.trial_remainder,self.t("Yes","بله") if s.restored else self.t("No","خیر"),s.remainder,f"{s.quotient:0{width}b}") for s in trace]
                self.flags.setText(f"{self.t('Quotient','خارج‌قسمت')} = {q}   |   {self.t('Remainder','باقی‌مانده')} = {r}"+suffix)
        except ValueError:
            self.status.setText(self.t("Invalid operand for selected base, width or signedness.","عدد ورودی با مبنا، طول کلمه یا علامت انتخاب‌شده سازگار نیست."))
            return
        self.status.clear()
        self.result=trace
        for row,(label,word) in enumerate((("A",a),("B",b))):
            for col,value in enumerate([label]+list(representations(word,width).values())):
                item=QTableWidgetItem(value)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.representation.setItem(row,col,item)
        self.stages.setRowCount(len(rows))
        for row,values in enumerate(rows):
            for col,value in enumerate(values):
                item=QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.stages.setItem(row,col,item)
