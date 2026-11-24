"""Mano Glass: portable Qt glass-inspired design tokens."""
PALETTES = {
    "dark": ("#11192c", "#17243a", "#283a56", "#edf5ff", "#a6b8d0", "#8bd5ff", "#405875"),
    "light": ("#e1ebfb", "#f6f9ff", "#d9e7f8", "#142b44", "#465e78", "#175fa9", "#a8bfdc"),
    "night": ("#241d25", "#30252b", "#48363b", "#f6e2d0", "#c7ad9e", "#f3bd89", "#69504a"),
}


def stylesheet(theme, glass_enabled=True):
    theme = theme if theme in PALETTES else "dark"
    bg, panel, raised, fg, muted, accent, border = PALETTES[theme]
    light = theme == "light"
    shine = "rgba(255,255,255,205)" if light else "rgba(255,255,255,38)"
    glass = "rgba(255,255,255,115)" if light else "rgba(15,24,43,125)" if theme == "dark" else "rgba(47,31,37,140)"
    rim = "rgba(255,255,255,235)" if light else "rgba(255,255,255,65)"
    gradient = f"qlineargradient(x1:0,y1:0,x2:0,y2:1,stop:0 {shine},stop:0.48 {glass},stop:1 {glass})"
    if not glass_enabled:
        glass, rim, gradient = panel, border, raised
    return f"""
    QWidget {{ color: {fg}; font-size: 13px; }}
    QMainWindow, QDialog, QMenu, QComboBox QAbstractItemView {{ background: {bg}; }}
    QWidget#glassRoot {{ background: transparent; }}
    QFrame#glassBar {{ background: {gradient}; border: 1px solid {rim}; border-radius: 18px; }}
    QLabel {{ background: transparent; }}
    QLabel#brand {{ font-size: 24px; font-weight: bold; color: {accent}; }}
    QLabel#subtitle, QLabel#muted {{ color: {muted}; }}
    QLabel#section {{ font-weight: bold; color: {accent}; padding: 3px 6px; }}
    QPlainTextEdit, QLineEdit, QTableWidget, QListWidget {{
        background: {panel}; border: 1px solid {border}; border-radius: 10px;
        selection-background-color: {accent}; selection-color: {bg}; padding: 5px;
    }}
    QComboBox, QPushButton {{
        background: {gradient}; border: 1px solid {rim};
        border-radius: 13px; padding: 8px 13px;
    }}
    QComboBox {{ padding-right: 20px; }}
    QPushButton:hover, QComboBox:hover {{ background: {raised}; border-color: {accent}; }}
    QPushButton:pressed {{ background: {panel}; border-color: {accent}; }}
    QPushButton:focus, QComboBox:focus, QLineEdit:focus {{ border: 2px solid {accent}; }}
    QPushButton:disabled {{ color: {muted}; }}
    QPushButton#primary {{ background: {accent}; color: {"#ffffff" if light else bg}; font-weight: bold; border: 1px solid {rim}; }}
    QTabBar::tab {{ background: {glass}; padding: 9px 16px; border: 1px solid transparent; border-radius: 13px; margin: 2px; }}
    QTabBar::tab:selected {{ background: {gradient}; border-color: {accent}; color: {accent}; }}
    QTabWidget::pane {{ background: {glass}; border: 1px solid {rim}; border-radius: 17px; }}
    QHeaderView::section {{ background: {raised}; color: {fg}; padding: 6px; border: none; }}
    QSplitter::handle {{ background: transparent; }}
    QToolTip {{ background: {panel}; color: {fg}; border: 1px solid {border}; }}
    QStatusBar {{ color: {muted}; background: transparent; }}
    """
