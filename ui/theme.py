"""Mano Glass: shared visual tokens and native Qt palette."""
PALETTES = {
    "dark": ("#101722", "#182331", "#243346", "#e7eff8", "#a3b4c8", "#8bcff2", "#3b4e64"),
    "light": ("#e8eef5", "#f9fbfe", "#e0e8f2", "#172b42", "#52667b", "#175c9c", "#a8bacd"),
    "night": ("#211d21", "#30272b", "#403237", "#f3e1d0", "#c6ad9d", "#edb984", "#67504b"),
}
SYNTAX = {
    "dark": ("#91c9f3", "#d4b4ef", "#a0b1c5"),
    "light": ("#195b9b", "#7545a1", "#52677c"),
    "night": ("#eac08d", "#d9a9c1", "#bda69a"),
}
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
    glass = "rgba(255,255,255,180)" if light else "rgba(22,32,46,205)" if theme=="dark" else "rgba(48,39,43,215)"
    shine = "rgba(255,255,255,235)" if light else "rgba(105,132,159,65)"
    rim = "rgba(255,255,255,245)" if light else "rgba(173,198,224,65)"
    gradient = f"qlineargradient(x1:0,y1:0,x2:0,y2:1,stop:0 {shine},stop:0.18 {glass},stop:1 {glass})"
    if not glass_enabled:
        glass,rim,gradient = panel,border,panel
    return f"""
    QWidget {{ color: {fg}; }}
    QMainWindow, QDialog, QMenu, QComboBox QAbstractItemView {{ background: {bg}; }}
    QWidget#glassRoot {{ background: transparent; }}
    QFrame#glassBar {{ background: {gradient}; border: 1px solid {rim}; border-radius: 15px; }}
    QFrame#editorPanel {{ background: {panel}; border: 1px solid {border}; border-radius: 12px; }}
    QLabel {{ background: transparent; }}
    QLabel#brand {{ font-size: 20px; font-weight: bold; color: {fg}; }}
    QLabel#subtitle, QLabel#muted {{ color: {muted}; }}
    QLabel#section {{ font-weight: bold; color: {fg}; padding: 3px 2px; }}
    QLabel[state="success"] {{ color: {good}; }}
    QLabel[state="error"] {{ color: {bad}; }}
    QLabel[state="neutral"] {{ color: {muted}; }}
    QPlainTextEdit, QLineEdit, QTableWidget, QListWidget, QSpinBox {{
        background: {panel}; border: 1px solid {border}; border-radius: 8px;
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
    QPushButton#primary {{ background: {accent}; color: {on_accent}; font-weight: bold; border: 1px solid {accent}; }}
    QPushButton#primary:hover {{ border-color: {fg}; }}
    QPushButton#primary:disabled {{ background: {raised}; color: {muted}; border-color: {border}; }}
    QTabBar::tab {{ background: transparent; padding: 8px 13px; border: 1px solid transparent; border-radius: 8px; margin: 2px; }}
    QTabBar::tab:selected {{ background: {raised}; border-color: {border}; color: {accent}; }}
    QTabWidget::pane {{ background: {glass}; border: 1px solid {border}; border-radius: 12px; }}
    QHeaderView::section {{ background: {raised}; color: {fg}; padding: 6px; border: none; }}
    QTableWidget {{ gridline-color: {border}; alternate-background-color: {raised}; }}
    QMenu {{ border: 1px solid {border}; padding: 5px; }}
    QMenu::item {{ padding: 7px 18px; border-radius: 5px; }}
    QMenu::item:selected {{ background: {raised}; color: {fg}; }}
    QSplitter::handle {{ background: transparent; }}
    QSplitter::handle:hover {{ background: {border}; }}
    QToolTip {{ background: {panel}; color: {fg}; border: 1px solid {border}; }}
    QStatusBar {{ color: {muted}; background: transparent; }}
    """
