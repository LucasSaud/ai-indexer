"""Output panel — lists written output files with open/reveal actions."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMenu,
    QVBoxLayout,
    QWidget,
)

_FORMAT_COLORS: dict[str, str] = {
    "toon": "#58a6ff",
    "json": "#3fb950",
    "html": "#d2a8ff",
    "md":   "#ffa657",
    "xml":  "#79c0ff",
    "dsl":  "#f0883e",
}


class OutputPanel(QWidget):
    """Shows written output files with context-menu actions (Open / Reveal)."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._paths: dict[str, Path] = {}
        self._build_ui()

    # ── UI ────────────────────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        title = QLabel("Output Files")
        title.setStyleSheet("color: #8b949e; font-size: 11px;")
        layout.addWidget(title)

        self._list = QListWidget()
        self._list.setStyleSheet(
            "QListWidget {"
            "  background-color: #161b22;"
            "  border: 1px solid #30363d;"
            "  border-radius: 4px;"
            "}"
            "QListWidget::item { padding: 4px 6px; color: #c9d1d9; }"
            "QListWidget::item:selected { background-color: #1f6feb; }"
        )
        self._list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self._list.customContextMenuRequested.connect(self._show_context_menu)
        self._list.doubleClicked.connect(self._open_selected)
        layout.addWidget(self._list)

    # ── Public API ────────────────────────────────────────────────────────────

    def add_file(self, fmt: str, path: Path) -> None:
        """Add a written output file row."""
        size_kb = path.stat().st_size / 1024 if path.exists() else 0
        label = f"[{fmt.upper()}]  {path.name}  ({size_kb:.1f} KB)"
        item = QListWidgetItem(label)
        item.setForeground(Qt.GlobalColor.white)
        item.setData(Qt.ItemDataRole.UserRole, str(path))
        item.setToolTip(str(path))
        self._list.addItem(item)
        self._paths[str(path)] = path

    def clear(self) -> None:
        self._list.clear()
        self._paths.clear()

    # ── Slots ─────────────────────────────────────────────────────────────────

    def _show_context_menu(self, pos: object) -> None:
        item = self._list.itemAt(pos)  # type: ignore[arg-type]
        if item is None:
            return
        path = Path(item.data(Qt.ItemDataRole.UserRole))
        menu = QMenu(self)
        open_act = menu.addAction("Open File")
        reveal_act = menu.addAction("Reveal in Finder")
        chosen = menu.exec(self._list.mapToGlobal(pos))  # type: ignore[arg-type]
        if chosen is open_act:
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(path)))
        elif chosen is reveal_act:
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(path.parent)))

    def _open_selected(self) -> None:
        items = self._list.selectedItems()
        if not items:
            return
        path = Path(items[0].data(Qt.ItemDataRole.UserRole))
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(path)))
