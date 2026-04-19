"""QApplication entry point — palette, Fusion theme, and main() for the GUI."""

from __future__ import annotations

import sys

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QApplication

from ai_indexer.gui.main_window import MainWindow


def build_dark_palette() -> QPalette:
    """Return a fully-populated dark QPalette (GitHub dark theme colours)."""
    palette = QPalette()

    palette.setColor(QPalette.ColorRole.Window,          QColor("#0d1117"))
    palette.setColor(QPalette.ColorRole.WindowText,      QColor("#c9d1d9"))
    palette.setColor(QPalette.ColorRole.Base,            QColor("#161b22"))
    palette.setColor(QPalette.ColorRole.AlternateBase,   QColor("#0d1117"))
    palette.setColor(QPalette.ColorRole.Text,            QColor("#c9d1d9"))
    palette.setColor(QPalette.ColorRole.BrightText,      QColor("#ffffff"))
    palette.setColor(QPalette.ColorRole.PlaceholderText, QColor("#484f58"))
    palette.setColor(QPalette.ColorRole.Button,          QColor("#21262d"))
    palette.setColor(QPalette.ColorRole.ButtonText,      QColor("#c9d1d9"))
    palette.setColor(QPalette.ColorRole.Highlight,       QColor("#1f6feb"))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#ffffff"))
    palette.setColor(QPalette.ColorRole.Link,            QColor("#58a6ff"))
    palette.setColor(QPalette.ColorRole.LinkVisited,     QColor("#a371f7"))
    palette.setColor(QPalette.ColorRole.Mid,             QColor("#30363d"))
    palette.setColor(QPalette.ColorRole.Dark,            QColor("#21262d"))
    palette.setColor(QPalette.ColorRole.Shadow,          QColor("#010409"))
    palette.setColor(QPalette.ColorRole.Midlight,        QColor("#161b22"))
    palette.setColor(QPalette.ColorRole.Light,           QColor("#21262d"))
    palette.setColor(QPalette.ColorRole.ToolTipBase,     QColor("#1c2128"))
    palette.setColor(QPalette.ColorRole.ToolTipText,     QColor("#c9d1d9"))

    disabled_text = QColor("#484f58")
    for role in (
        QPalette.ColorRole.WindowText,
        QPalette.ColorRole.Text,
        QPalette.ColorRole.ButtonText,
    ):
        palette.setColor(QPalette.ColorGroup.Disabled, role, disabled_text)

    return palette


def main() -> None:
    """CLI entry point for ``ai-indexer-gui``."""
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    app.setApplicationName("AI Indexer")
    app.setApplicationVersion("0.0.7")
    app.setOrganizationName("ai-indexer")
    app.setStyle("Fusion")
    app.setPalette(build_dark_palette())

    app.setStyleSheet(
        "QToolTip { background-color: #1c2128; color: #c9d1d9; border: 1px solid #30363d; }"
        "QMenuBar { background-color: #161b22; color: #c9d1d9;"
        "           border-bottom: 1px solid #30363d; }"
        "QMenuBar::item:selected { background-color: #21262d; }"
        "QMenu { background-color: #161b22; color: #c9d1d9; border: 1px solid #30363d; }"
        "QMenu::item:selected { background-color: #1f6feb; }"
        "QScrollBar:vertical { background: #0d1117; width: 8px; }"
        "QScrollBar::handle:vertical { background: #30363d; border-radius: 4px; min-height: 20px; }"
        "QScrollBar:horizontal { background: #0d1117; height: 8px; }"
        "QScrollBar::handle:horizontal { background: #30363d; border-radius: 4px; min-width: 20px; }"
        "QScrollBar::add-line, QScrollBar::sub-line { width: 0; height: 0; }"
    )

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
