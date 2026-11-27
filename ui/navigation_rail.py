"""A single responsive navigation control over existing lab pages.

The underlying QTabWidget remains the state owner. The rail does not create,
reload or duplicate a page. In compact mode the original tabs become visible.
"""
from PySide6.QtCore import Qt,QSize,QSignalBlocker
from PySide6.QtGui import QPalette
from PySide6.QtWidgets import (QFrame,QVBoxLayout,QHBoxLayout,QLabel,QPushButton,
    QListWidget,QListWidgetItem,QAbstractItemView)
from ui.icons import icon
from ui.motion import MotionButton


class NavigationRail(QFrame):
    def __init__(self,tabs,settings,key,title,icons,fa=False):
        super().__init__()
        self.tabs=tabs
        self.settings=settings
        self.key="navigation/"+key+"/compact"
        self.fa=fa
        self.names=tuple(icons)
        if len(self.names)!=tabs.count():
            raise ValueError("One navigation icon per page is required")
        self.setObjectName("navigationRail")
        box=QVBoxLayout(self);box.setContentsMargins(8,10,8,10);box.setSpacing(8)
        row=QHBoxLayout();row.setContentsMargins(0,0,0,0)
        self.heading=QLabel(title);self.heading.setObjectName("eyebrow")
        row.addWidget(self.heading,1)
        self.toggle=MotionButton();self.toggle.setObjectName("railToggle")
        self.toggle.setFixedSize(32,32)
        self.toggle.setCheckable(True)
        self.toggle.setAutoDefault(False)
        row.addWidget(self.toggle)
        box.addLayout(row)
        self.list=QListWidget();self.list.setObjectName("navigationList")
        self.list.setAccessibleName("مسیرهای آزمایشگاه" if fa else "Laboratory pages")
        self.list.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.list.setIconSize(QSize(18,18))
        self.list.setSpacing(2)
        self.list.setTextElideMode(Qt.TextElideMode.ElideRight)
        color=self.palette().color(QPalette.ColorRole.WindowText).name()
        for index,name in enumerate(self.names):
            text=tabs.tabText(index)
            item=QListWidgetItem(icon(name,color),text)
            item.setToolTip(text)
            item.setData(Qt.ItemDataRole.UserRole,index)
            self.list.addItem(item)
        box.addWidget(self.list,1)
        self.list.currentRowChanged.connect(self._navigate)
        tabs.currentChanged.connect(self._sync)
        self.toggle.toggled.connect(self.set_compact)
        self.toggle.setIcon(icon("sidebar",color))
        self._sync(tabs.currentIndex())
        self.set_compact(settings.value(self.key,False,type=bool))

    def _navigate(self,index):
        if 0<=index<self.tabs.count():
            self.tabs.setCurrentIndex(index)

    def _sync(self,index):
        with QSignalBlocker(self.list):
            self.list.setCurrentRow(index)

    def set_compact(self,compact):
        self.compact=bool(compact)
        with QSignalBlocker(self.toggle):
            self.toggle.setChecked(self.compact)
        self.heading.setVisible(not self.compact)
        self.list.setVisible(not self.compact)
        self.tabs.tabBar().setVisible(self.compact)
        self.setFixedWidth(50 if self.compact else 220)
        text=("باز کردن نوار ابزار" if self.fa else "Expand navigation") if self.compact else ("جمع کردن نوار ابزار" if self.fa else "Collapse navigation")
        self.toggle.setAccessibleName(text);self.toggle.setToolTip(text)
        self.settings.setValue(self.key,self.compact)
        self._sync(self.tabs.currentIndex())
