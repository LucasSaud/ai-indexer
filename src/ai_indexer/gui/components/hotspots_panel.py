"""Hotspots panel — top-N files by priority score."""

from __future__ import annotations

from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QLabel,
    QListWidget,
    QListWidgetItem,
    QVBoxLayout,
    QWidget,
)


class HotspotsPanel(QWidget):
    """Displays top-15 files sorted by priority_score."""

    TOP_N = 15

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._build_ui()

    # ── UI ────────────────────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        self._title = QLabel("Top Hotspots")
        self._title.setStyleSheet(
            "color: #f0883e; font-size: 12px; font-weight: bold; padding: 2px;"
        )
        layout.addWidget(self._title)

        self._list = QListWidget()
        self._list.setStyleSheet(
            "QListWidget {"
            "  background-color: #161b22;"
            "  border: 1px solid #30363d;"
            "  border-radius: 4px;"
            "}"
            "QListWidget::item { padding: 4px 6px; color: #c9d1d9; font-size: 11px; }"
            "QListWidget::item:selected { background-color: #1f6feb; }"
            "QListWidget::item:hover { background-color: #21262d; }"
        )
        self._list.setWordWrap(True)
        layout.addWidget(self._list)

    # ── Public API ────────────────────────────────────────────────────────────

    def populate(self, hotspots: list[dict[str, Any]]) -> None:
        """Populate from output_data['hotspots'] — already sorted by priority_score."""
        self._list.clear()
        for rank, entry in enumerate(hotspots[: self.TOP_N], start=1):
            file_path = entry.get("file", "")
            score = entry.get("priority_score", 0)
            blast = entry.get("blast_radius", 0)
            refactor = entry.get("refactor_effort", 0.0)
            short = file_path.split("/")[-1] if "/" in file_path else file_path
            text = f"{rank:2d}. {short}  ·  score={score}  blast={blast}  refactor={refactor:.2f}"
            item = QListWidgetItem(text)
            item.setData(Qt.ItemDataRole.UserRole, file_path)
            item.setToolTip(file_path)
            self._list.addItem(item)
        self._title.setText(f"Top Hotspots ({min(len(hotspots), self.TOP_N)})")

    def clear(self) -> None:
        self._list.clear()
        self._title.setText("Top Hotspots")
