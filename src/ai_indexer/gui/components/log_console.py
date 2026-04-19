"""Log console — streaming read-only QPlainTextEdit for engine output."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QTextCursor
from PySide6.QtWidgets import QPlainTextEdit, QVBoxLayout, QWidget, QLabel


_MAX_LINES = 5000


class LogConsole(QWidget):
    """Collapsible log panel with a monospace streaming text view."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._build_ui()

    # ── UI ────────────────────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        title = QLabel("Log")
        title.setStyleSheet("color: #8b949e; font-size: 11px; padding: 2px 6px;")
        layout.addWidget(title)

        self._edit = QPlainTextEdit()
        self._edit.setReadOnly(True)
        self._edit.setMaximumBlockCount(_MAX_LINES)
        font = QFont("Menlo")
        if not font.exactMatch():
            font = QFont("Monaco")
        if not font.exactMatch():
            font = QFont("Courier New")
        font.setPointSize(11)
        self._edit.setFont(font)
        self._edit.setStyleSheet(
            "QPlainTextEdit {"
            "  background-color: #0d1117;"
            "  color: #c9d1d9;"
            "  border: 1px solid #30363d;"
            "  border-radius: 4px;"
            "  padding: 4px;"
            "}"
        )
        layout.addWidget(self._edit)

    # ── Public API ────────────────────────────────────────────────────────────

    def append_line(self, text: str) -> None:
        """Append a log line and auto-scroll to the bottom."""
        self._edit.appendPlainText(text)
        cursor = self._edit.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self._edit.setTextCursor(cursor)

    def clear(self) -> None:
        self._edit.clear()
