"""Independent design tokens for the three desktop themes."""
PALETTES = {
    "dark": ("#101722", "#172131", "#223047", "#e1e9f4", "#9eafc4", "#69b8ff", "#33435b"),
    "light": ("#edf2f8", "#ffffff", "#e4ebf5", "#17283d", "#52647b", "#1761b6", "#c7d3e4"),
    "night": ("#211d19", "#2c2621", "#3c3229", "#efdbc1", "#baa48d", "#e0ad70", "#514435"),
}


def stylesheet(theme):
    bg, panel, raised, fg, muted, accent, border = PALETTES.get(theme, PALETTES["dark"])
    return f"""
    QWidget {{ background: {bg}; color: {fg}; font-size: 13px; }}
    QMainWindow, QDialog {{ background: {bg}; }}
    QLabel#brand {{ font-size: 24px; font-weight: bold; color: {accent}; }}
    QLabel#subtitle, QLabel#muted {{ color: {muted}; }}
    QLabel#section {{ font-weight: bold; color: {accent}; }}
    QPlainTextEdit, QLineEdit, QComboBox, QTableWidget, QListWidget {{
        background: {panel}; border: 1px solid {border}; border-radius: 6px;
        selection-background-color: {accent}; selection-color: {bg}; padding: 5px;
    }}
    QPushButton {{ background: {raised}; border: 1px solid {border};
        border-radius: 6px; padding: 7px 12px; }}
    QPushButton:hover {{ border-color: {accent}; }}
    QPushButton:disabled {{ color: {muted}; }}
    QPushButton#primary {{ background: {accent}; color: {bg}; font-weight: bold; }}
    QTabBar::tab {{ background: {panel}; padding: 8px 14px; border-bottom: 2px solid {border}; }}
    QTabBar::tab:selected {{ border-bottom: 2px solid {accent}; }}
    QTabWidget::pane {{ border: 1px solid {border}; border-radius: 6px; }}
    QHeaderView::section {{ background: {raised}; color: {fg}; padding: 5px; border: none; }}
    QSplitter::handle {{ background: {border}; }}
    QProgressBar {{ border: 1px solid {border}; border-radius: 4px; text-align: center; }}
    QProgressBar::chunk {{ background: {accent}; }}
    QToolTip {{ background: {panel}; color: {fg}; border: 1px solid {border}; }}
    """
