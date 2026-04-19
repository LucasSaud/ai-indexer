"""Files table — sortable QTableWidget showing FileMetadata for every file."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QBrush, QColor, QDesktopServices
from PySide6.QtWidgets import (
    QAbstractItemView,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

# Column definitions: (header_label, metadata_key_or_extractor)
_COLUMNS: list[tuple[str, str]] = [
    ("File",           "file"),
    ("Domain",         "domain_value"),
    ("Layer",          "layer"),
    ("Criticality",    "criticality"),
    ("Complexity",     "complexity_label"),
    ("Priority",       "priority_score"),
    ("Blast Radius",   "blast_radius"),
    ("Refactor",       "refactor_effort"),
    ("Fan In",         "fan_in"),
    ("Fan Out",        "fan_out"),
    ("Warnings",       "warning_count"),
    ("Entrypoint",     "entrypoint"),
]

_CRITICALITY_COLORS: dict[str, str] = {
    "critical": "#3d1a1a",
    "high":     "#3d2a0a",
    "medium":   "#1a2a1a",
    "low":      "#0d1117",
    "minimal":  "#0d1117",
}


class FilesTable(QWidget):
    """Sortable table of all analysed files."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._build_ui()

    # ── UI ────────────────────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        self._label = QLabel("Files")
        self._label.setStyleSheet(
            "color: #58a6ff; font-size: 12px; font-weight: bold; padding: 4px 6px;"
        )
        layout.addWidget(self._label)

        self._table = QTableWidget(0, len(_COLUMNS))
        self._table.setHorizontalHeaderLabels([c[0] for c in _COLUMNS])
        self._table.setSortingEnabled(True)
        self._table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self._table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._table.setAlternatingRowColors(False)
        self._table.verticalHeader().setVisible(False)
        self._table.horizontalHeader().setStretchLastSection(False)
        self._table.setStyleSheet(
            "QTableWidget {"
            "  background-color: #0d1117;"
            "  gridline-color: #21262d;"
            "  color: #c9d1d9;"
            "  font-size: 11px;"
            "  border: none;"
            "}"
            "QTableWidget::item { padding: 3px 6px; border: none; }"
            "QTableWidget::item:selected { background-color: #1f6feb; }"
            "QHeaderView::section {"
            "  background-color: #161b22;"
            "  color: #8b949e;"
            "  border: 1px solid #21262d;"
            "  padding: 4px;"
            "  font-size: 11px;"
            "}"
        )
        self._table.doubleClicked.connect(self._open_file)
        layout.addWidget(self._table)

    # ── Public API ────────────────────────────────────────────────────────────

    def populate(self, files_snapshot: dict[str, dict[str, Any]], root: Path) -> None:
        """Populate table from the files snapshot dict."""
        self._table.setSortingEnabled(False)
        self._table.setRowCount(0)

        rows = sorted(files_snapshot.items())
        self._table.setRowCount(len(rows))

        for row_idx, (path, meta) in enumerate(rows):
            values = self._extract_values(path, meta, root)
            bg_color = QColor(_CRITICALITY_COLORS.get(meta.get("criticality", ""), "#0d1117"))
            blast = meta.get("blast_radius", 0)
            if isinstance(blast, int) and blast > 20:
                bg_color = QColor("#2a1f0a")  # orange tint for high blast radius

            for col_idx, value in enumerate(values):
                item = self._make_item(value)
                item.setBackground(QBrush(bg_color))
                self._table.setItem(row_idx, col_idx, item)

        self._table.resizeColumnsToContents()
        self._table.setSortingEnabled(True)
        self._label.setText(f"Files ({len(rows)})")

    def clear(self) -> None:
        self._table.setRowCount(0)
        self._label.setText("Files")

    # ── Private ───────────────────────────────────────────────────────────────

    def _extract_values(
        self, path: str, meta: dict[str, Any], root: Path
    ) -> list[Any]:
        short_path = path
        # Shorten if it starts with root path
        try:
            short_path = str(Path(path).relative_to(root))
        except ValueError:
            pass

        domain_raw = meta.get("domain", {})
        domain_value = (
            domain_raw.get("value", "") if isinstance(domain_raw, dict) else str(domain_raw)
        )
        warnings_count = len(meta.get("warnings", []))

        return [
            short_path,
            domain_value,
            meta.get("layer", ""),
            meta.get("criticality", ""),
            meta.get("complexity_label", ""),
            meta.get("priority_score", 0),
            meta.get("blast_radius", 0),
            round(meta.get("refactor_effort", 0.0), 2),
            meta.get("fan_in", 0),
            meta.get("fan_out", 0),
            warnings_count,
            "yes" if meta.get("entrypoint") else "",
        ]

    def _make_item(self, value: Any) -> QTableWidgetItem:
        """Create a sortable table item that sorts numerically for numbers."""
        item = QTableWidgetItem()
        if isinstance(value, (int, float)):
            item.setData(Qt.ItemDataRole.DisplayRole, value)
        else:
            item.setText(str(value))
        return item

    def _open_file(self) -> None:
        row = self._table.currentRow()
        if row < 0:
            return
        file_item = self._table.item(row, 0)
        if file_item is None:
            return
        path_str = file_item.text()
        path = Path(path_str)
        if path.exists():
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(path.resolve())))
