"""Offline catalog and explicit local study progress; no new engine."""
import json
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QDialog,QVBoxLayout,QHBoxLayout,QLabel,QComboBox,QLineEdit,
    QListWidget,QListWidgetItem,QPushButton,QCheckBox,QSplitter,QWidget,QProgressBar,QFrame)
from learning_catalog import CHAPTERS,TOOLS,BY_ID,BY_CHAPTER,search_tools,clean_progress


class LearningCenter(QDialog):
    def __init__(self,parent):
        super().__init__(parent)
        self.fa=parent.language=="fa"
        self.settings=parent.settings
        self.selected=None
        self.practiced=set(self.read_progress())
        self.setWindowTitle("Mano Studio — "+self.t("Learning Center","مرکز یادگیری"))
        self.resize(920,590)
        layout=QVBoxLayout(self)
        title=QLabel(self.t("Explore the Mano curriculum","کتاب مانو را تعاملی یاد بگیرید"))
        title.setObjectName("brand");layout.addWidget(title)
        subtitle=QLabel(self.t("Open an existing interactive tool, or inspect what remains in each chapter. Practice progress is your own checklist, not textbook completion.",
            "یک ابزار تعاملی موجود را باز کنید یا بخش‌های باقی‌مانده هر فصل را ببینید. پیشرفت تمرین، چک‌لیست شخصی شماست، نه تکمیل کتاب."))
        subtitle.setWordWrap(True);layout.addWidget(subtitle)
        row=QHBoxLayout()
        self.search=QLineEdit();self.search.setPlaceholderText(self.t("Search tools, chapters or keywords…","جست‌وجوی ابزار، فصل یا کلیدواژه…"))
        self.search.setAccessibleName(self.t("Search curriculum","جست‌وجوی کتاب"));row.addWidget(self.search,1)
        self.chapter=QComboBox()
        self.chapter.addItem(self.t("All 13 chapters","همه ۱۳ فصل"),0)
        for ch in CHAPTERS:self.chapter.addItem(f"{ch.number} · {ch.title[self.fa]}",ch.number)
        row.addWidget(self.chapter)
        self.remaining=QCheckBox(self.t("Not yet practiced","تمرین‌نشده"));row.addWidget(self.remaining)
        layout.addLayout(row)
        self.progress=QProgressBar();self.progress.setRange(0,len(TOOLS));self.progress.setTextVisible(False)
        self.progress.setAccessibleName(self.t("Personal practice progress","پیشرفت شخصی تمرین"))
        row=QHBoxLayout();row.addWidget(self.progress,1)
        self.progress_label=QLabel();row.addWidget(self.progress_label);layout.addLayout(row)
        split=QSplitter(Qt.Orientation.Horizontal)
        self.list=QListWidget();self.list.setAccessibleName(self.t("Available tools","ابزارهای موجود"));split.addWidget(self.list)
        detail=QFrame();detail.setObjectName("editorPanel");box=QVBoxLayout(detail)
        self.detail_title=QLabel();self.detail_title.setObjectName("brand");self.detail_title.setWordWrap(True);box.addWidget(self.detail_title)
        self.detail_chapter=QLabel();self.detail_chapter.setWordWrap(True);box.addWidget(self.detail_chapter)
        self.task=QLabel();self.task.setWordWrap(True);box.addWidget(self.task)
        self.gap=QLabel();self.gap.setWordWrap(True);box.addWidget(self.gap)
        box.addStretch()
        self.mark=QPushButton();self.mark.clicked.connect(self.toggle_practiced);box.addWidget(self.mark)
        self.open_button=QPushButton(self.t("Open tool","باز کردن ابزار"));self.open_button.setObjectName("primary")
        self.open_button.clicked.connect(self.launch);box.addWidget(self.open_button)
        split.addWidget(detail);split.setSizes([450,400]);layout.addWidget(split,1)
        self.search.textChanged.connect(self.refresh)
        self.chapter.currentIndexChanged.connect(self.refresh)
        self.remaining.toggled.connect(self.refresh)
        self.list.currentItemChanged.connect(self.show_detail)
        self.list.itemDoubleClicked.connect(lambda _:self.launch())
        self.refresh();self.search.setFocus()

    def t(self,en,fa):return fa if self.fa else en

    def read_progress(self):
        try:
            data=json.loads(self.settings.value("learning/practiced","[]",type=str))
            return clean_progress(data) if isinstance(data,list) else ()
        except (ValueError,TypeError):return ()

    def current_id(self):
        item=self.list.currentItem()
        return item.data(Qt.ItemDataRole.UserRole) if item else None

    def refresh(self,*_):
        current=self.current_id()
        self.list.clear()
        matches=search_tools(self.search.text(),self.chapter.currentData(),self.practiced,self.remaining.isChecked())
        selected_row=0
        for i,tool in enumerate(matches):
            prefix="✓  " if tool.id in self.practiced else ""
            item=QListWidgetItem(f"{prefix}{tool.chapter} · {tool.title[self.fa]}")
            item.setData(Qt.ItemDataRole.UserRole,tool.id)
            self.list.addItem(item)
            if tool.id==current:selected_row=i
        if matches:self.list.setCurrentRow(selected_row)
        self.progress.setValue(len(self.practiced))
        self.progress_label.setText(f"{len(self.practiced)} / {len(TOOLS)} "+self.t("practiced","تمرین‌شده"))
        self.show_detail()

    def show_detail(self,*_):
        tool=BY_ID.get(self.current_id())
        chapter=BY_CHAPTER.get(tool.chapter if tool else self.chapter.currentData())
        self.open_button.setEnabled(tool is not None);self.mark.setEnabled(tool is not None)
        if tool:
            self.detail_title.setText(tool.title[self.fa])
            self.task.setText(self.t("Try this: ","تمرین پیشنهادی: ")+tool.task[self.fa])
            self.mark.setText(self.t("Undo practice mark","لغو علامت تمرین") if tool.id in self.practiced else self.t("Mark as practiced","علامت‌گذاری به‌عنوان تمرین‌شده"))
        else:
            self.detail_title.setText(chapter.title[self.fa] if chapter else self.t("No matching tools","ابزار مطابق یافت نشد"))
            self.task.setText(self.t("No matching interactive tool. Change the search or chapter filter.","ابزار تعاملی مطابق یافت نشد. جست‌وجو یا فیلتر فصل را تغییر دهید."))
            self.mark.setText(self.t("Mark as practiced","علامت‌گذاری به‌عنوان تمرین‌شده"))
        if chapter:
            self.detail_chapter.setText(self.t("Chapter ","فصل ")+str(chapter.number)+" · "+chapter.title[self.fa])
            self.gap.setText(self.t("Remaining coverage: ","پوشش باقی‌مانده: ")+chapter.gap[self.fa])
        else:self.detail_chapter.clear();self.gap.clear()

    def toggle_practiced(self):
        key=self.current_id()
        if key not in BY_ID:return
        if key in self.practiced:self.practiced.remove(key)
        else:self.practiced.add(key)
        self.settings.setValue("learning/practiced",json.dumps(clean_progress(self.practiced)))
        self.refresh()

    def launch(self):
        tool=BY_ID.get(self.current_id())
        if tool:
            self.selected=tool
            self.accept()
