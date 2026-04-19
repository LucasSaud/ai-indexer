"""Warnings panel — architectural and security warnings tree."""

from __future__ import annotations

from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QLabel,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)


class WarningsPanel(QWidget):
    """Two-level tree: Architectural Warnings and Security Warnings."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._build_ui()

    # ── UI ────────────────────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        self._title = QLabel("Warnings")
        self._title.setStyleSheet(
            "color: #d29922; font-size: 12px; font-weight: bold; padding: 2px;"
        )
        layout.addWidget(self._title)

        self._tree = QTreeWidget()
        self._tree.setHeaderHidden(True)
        self._tree.setStyleSheet(
            "QTreeWidget {"
            "  background-color: #161b22;"
            "  border: 1px solid #30363d;"
            "  border-radius: 4px;"
            "  color: #c9d1d9;"
            "  font-size: 11px;"
            "}"
            "QTreeWidget::item { padding: 2px 4px; }"
            "QTreeWidget::item:selected { background-color: #1f6feb; }"
            "QTreeWidget::item:hover { background-color: #21262d; }"
        )
        layout.addWidget(self._tree)

    # ── Public API ────────────────────────────────────────────────────────────

    def populate(self, files_snapshot: dict[str, dict[str, Any]]) -> None:
        """Build the tree from the files snapshot produced by engine_worker."""
        self._tree.clear()

        arch_root = QTreeWidgetItem(self._tree, ["⚠  Architectural Warnings"])
        arch_root.setForeground(0, Qt.GlobalColor.yellow)
        arch_root.setExpanded(True)

        sec_root = QTreeWidgetItem(self._tree, ["🔐  Security Warnings"])
        sec_root.setForeground(0, Qt.GlobalColor.red)
        sec_root.setExpanded(True)

        arch_count = 0
        sec_count = 0

        for path, meta in sorted(files_snapshot.items()):
            warnings: list[str] = meta.get("warnings", [])
            if not warnings:
                continue

            arch_warns = [
                w for w in warnings
                if not any(k in w.lower() for k in ("secret", "credential", "hardcoded", "token"))
            ]
            sec_warns = [
                w for w in warnings
                if any(k in w.lower() for k in ("secret", "credential", "hardcoded", "token"))
            ]

            short = path.split("/")[-1] if "/" in path else path

            if arch_warns:
                file_item = QTreeWidgetItem(arch_root, [short])
                file_item.setToolTip(0, path)
                for w in arch_warns[:5]:
                    QTreeWidgetItem(file_item, [w])
                arch_count += len(arch_warns)

            if sec_warns:
                file_item = QTreeWidgetItem(sec_root, [short])
                file_item.setToolTip(0, path)
                for w in sec_warns[:5]:
                    QTreeWidgetItem(file_item, [w])
                sec_count += len(sec_warns)

        arch_root.setText(0, f"⚠  Architectural Warnings ({arch_count})")
        sec_root.setText(0, f"🔐  Security Warnings ({sec_count})")
        self._title.setText(f"Warnings ({arch_count + sec_count} total)")

    def clear(self) -> None:
        self._tree.clear()
        self._title.setText("Warnings")
