"""Mano Glass: shared visual tokens and native Qt palette."""
PALETTES = {
    "dark": ("#10142b", "#171e38", "#263358", "#f0f4ff", "#b0bedb", "#80dfff", "#435784"),
    "light": ("#e9edfa", "#fbfcff", "#e2e8fa", "#19284b", "#4e6180", "#2456af", "#a3b2d4"),
    "night": ("#211d21", "#30272b", "#403237", "#f3e1d0", "#c6ad9d", "#edb984", "#67504b"),
}
SYNTAX = {
    "dark": ("#83ddff", "#e6b0ff", "#aab8d5"),
    "light": ("#195b9b", "#7545a1", "#52677c"),
    "night": ("#eac08d", "#d9a9c1", "#bda69a"),
}
SPACING = (4, 8, 12, 16, 24, 32)
RADIUS = {"small":6,"control":9,"panel":14,"shell":16}
TYPE = {"caption":13,"body":14,"section":16,"title":22,"hero":28}

STATUS = {
    "dark": ("#9ed9b8", "#ffb5ab"),
    "light": ("#176942", "#a62f36"),
    "night": ("#c3d5a0", "#ffb3a5"),
}


def apply_theme(app, theme, glass_enabled=True):
    from PySide6.QtGui import QColor, QPalette
    theme = theme if theme in PALETTES else "dark"
    bg,panel,raised,fg,muted,accent,border = PALETTES[theme]
    palette = QPalette()
    roles = QPalette.ColorRole
    for role, value in [(roles.Window,bg),(roles.WindowText,fg),(roles.Base,panel),
                        (roles.AlternateBase,raised),(roles.Text,fg),(roles.Button,raised),
                        (roles.ButtonText,fg),(roles.Highlight,accent),
                        (roles.HighlightedText,"#ffffff" if theme=="light" else bg),
                        (roles.PlaceholderText,muted),(roles.Mid,muted),
                        (roles.ToolTipBase,panel),(roles.ToolTipText,fg)]:
        palette.setColor(role,QColor(value))
    for role in (roles.Text,roles.WindowText,roles.ButtonText):
        palette.setColor(QPalette.ColorGroup.Disabled,role,QColor(muted))
    app.setPalette(palette)
    app.setStyleSheet(stylesheet(theme,glass_enabled))


def stylesheet(theme, glass_enabled=True):
    theme = theme if theme in PALETTES else "dark"
    bg,panel,raised,fg,muted,accent,border = PALETTES[theme]
    good,bad = STATUS[theme]
    light = theme == "light"
    on_accent = "#ffffff" if light else bg
    glass = "rgba(255,255,255,180)" if light else "rgba(27,31,65,208)" if theme=="dark" else "rgba(48,39,43,215)"
    shine = "rgba(255,255,255,235)" if light else "rgba(137,108,237,88)"
    rim = "rgba(255,255,255,245)" if light else "rgba(153,179,255,100)"
    gradient = f"qlineargradient(x1:0,y1:0,x2:0,y2:1,stop:0 {shine},stop:0.18 {glass},stop:1 {glass})"
    action = "qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #80dfff,stop:1 #d2b1ff)" if theme == "dark" and glass_enabled else accent
    editor_glass = f"qlineargradient(x1:0,y1:0,x2:0,y2:1,stop:0 {raised},stop:0.18 {panel},stop:1 {panel})" if glass_enabled else panel
    if not glass_enabled:
        glass,rim,gradient = panel,border,panel
    return f"""
    QWidget {{ color: {fg}; }}
    QMainWindow, QDialog, QMenu, QComboBox QAbstractItemView {{ background: {bg}; }}
    QWidget#glassRoot {{ background: transparent; }}
    QFrame#glassBar {{ background: {gradient}; border: 1px solid {rim}; border-radius: {RADIUS["shell"]}px; }}
    QFrame#editorPanel {{ background: {panel}; border: 1px solid {border}; border-radius: {RADIUS["panel"]}px; }}
    QFrame#editorPanel[workspacePane="true"] {{ background: {editor_glass}; border-radius: {RADIUS["panel"]}px; }}
    QLabel {{ background: transparent; }}
    QLabel#workspaceHeading {{ font-size: {TYPE["section"]}px; font-weight: 600; color: {fg}; padding: 3px 2px; }}
    QLabel#versionChip {{ background: {raised}; color: {accent}; border: 1px solid {border}; border-radius: 7px; padding: 2px 7px; font-size: {TYPE["caption"]}px; font-weight: 600; }}
    QPushButton#academicAction {{ color: {accent}; border-color: {accent}; font-weight: 600; }}
    QPushButton#academicAction:hover {{ background: {raised}; border-color: {fg}; }}
    QLabel#brand {{ font-size: {TYPE["title"]}px; font-weight: 600; color: {fg}; }}
    QLabel#hero {{ font-size: {TYPE["hero"]}px; font-weight: 600; color: {fg}; }}
    QLabel#metric {{ font-size: 24px; font-weight: 600; color: {fg}; }}
    QLabel#eyebrow {{ font-size: {TYPE["caption"]}px; font-weight: 600; color: {muted}; }}
    QLabel#learningTask {{ font-size: {TYPE["section"]}px; color: {fg}; }}
    QLabel#subtitle, QLabel#muted {{ color: {muted}; }}
    QLabel#section {{ font-weight: bold; color: {fg}; padding: 3px 2px; }}
    QLabel[state="success"] {{ color: {good}; }}
    QLabel[state="error"] {{ color: {bad}; }}
    QLabel[state="neutral"] {{ color: {muted}; }}
    QPlainTextEdit, QLineEdit, QTableWidget, QListWidget, QSpinBox {{
        background: {panel}; border: 1px solid {border}; border-radius: {RADIUS["control"]}px;
        selection-background-color: {accent}; selection-color: {on_accent}; padding: 5px;
    }}
    QPlainTextEdit#workspaceCode {{ border: 1px solid transparent; border-radius: 6px; padding: 2px; }}
    QPlainTextEdit#workspaceCode:focus {{ border-color: {accent}; }}
    QComboBox, QPushButton {{
        background: {panel}; border: 1px solid {border};
        border-radius: 8px; padding: 7px 12px; min-height: 18px;
    }}
    QComboBox {{ padding-right: 18px; }}
    QPushButton:hover, QComboBox:hover {{ background: {raised}; border-color: {accent}; }}
    QPushButton:pressed, QPushButton:checked {{ background: {raised}; border-color: {accent}; }}
    QPushButton:focus, QComboBox:focus, QLineEdit:focus, QSpinBox:focus {{ border-color: {accent}; }}
    QPushButton:disabled {{ color: {muted}; background: {panel}; border-color: {border}; }}
    QPushButton#primary {{ background: {action}; color: {on_accent}; font-weight: bold; border: 1px solid {accent}; }}
    QPushButton#primary:hover {{ border-color: {fg}; }}
    QPushButton#primary:disabled {{ background: {raised}; color: {muted}; border-color: {border}; }}
    QPushButton#learnAction {{ color: {accent}; border-color: {accent}; font-weight: 600; }}
    QFrame#navigationRail {{ background: {gradient}; border: 1px solid {rim}; border-radius: {RADIUS["shell"]}px; }}
    QListWidget#navigationList {{ background: transparent; border: 1px solid transparent; padding: 2px; outline: none; }}
    QListWidget#navigationList::item {{ padding: 10px 7px; border: 1px solid transparent; border-radius: {RADIUS["control"]}px; }}
    QListWidget#navigationList::item:hover {{ background: {raised}; }}
    QListWidget#navigationList::item:selected {{ background: {raised}; border-color: {accent}; color: {fg}; }}
    QListWidget#navigationList:focus {{ border-color: {accent}; }}
    QPushButton#railToggle {{ padding: 2px; background: transparent; }}
    QPushButton#railToggle:hover {{ background: {raised}; }}
    QListWidget#learningList {{ padding: 5px; outline: none; }}
    QListWidget#learningList::item {{ padding: 9px 10px; margin: 2px 1px; border-radius: {RADIUS["control"]}px; border: 1px solid transparent; }}
    QListWidget#learningList::item:hover {{ background: {raised}; }}
    QListWidget#learningList::item:selected {{ background: {raised}; border-color: {accent}; color: {fg}; }}
    QListWidget#learningList:focus {{ border-color: {accent}; }}
    QProgressBar {{ border: 0; background: {raised}; border-radius: 4px; min-height: 8px; max-height: 8px; }}
    QProgressBar::chunk {{ background: {action}; border-radius: 4px; }}
    QTabBar::tab {{ background: transparent; padding: 8px 13px; border: 1px solid transparent; border-radius: 8px; margin: 2px; }}
    QTabBar::tab:selected {{ background: {raised}; border-color: {border}; color: {accent}; }}
    QTabBar::tab:hover {{ background: {raised}; }}
    QTabBar::tab:focus {{ border-color: {accent}; }}
    QTabWidget::pane {{ background: {glass}; border: 1px solid {border}; border-radius: 12px; }}
    QHeaderView::section {{ background: {raised}; color: {fg}; padding: 6px; border: none; }}
    QTableWidget::item {{ padding: 3px; }}
    QTableWidget {{ gridline-color: {border}; alternate-background-color: {raised}; }}
    QMenu {{ border: 1px solid {border}; padding: 5px; }}
    QMenu::item {{ padding: 7px 18px; border-radius: 5px; }}
    QMenu::item:selected {{ background: {raised}; color: {fg}; }}
    QSplitter::handle {{ background: transparent; }}
    QSplitter::handle:hover {{ background: {border}; }}
    QToolTip {{ background: {panel}; color: {fg}; border: 1px solid {border}; }}
    QStatusBar {{ color: {muted}; background: transparent; }}
    """
