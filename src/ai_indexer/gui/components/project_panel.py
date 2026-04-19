"""Project panel — path selector, format checkboxes, and Run button."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

_FORMATS: list[str] = ["toon", "json", "html", "md", "xml", "dsl"]


class ProjectPanel(QWidget):
    """Left-side control panel.

    Signals
    -------
    run_requested(root, options) — emitted when the user clicks "Run Analysis".
    """

    run_requested = Signal(object, dict)  # (Path, options dict)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._instruction_file = ""
        self._build_ui()

    # ── UI ────────────────────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(10)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # ── Project path ──────────────────────────────────────────────────────
        path_box = QGroupBox("Project Directory")
        path_box.setStyleSheet(self._group_style())
        path_layout = QVBoxLayout(path_box)

        self._path_label = QLabel("(none selected)")
        self._path_label.setWordWrap(True)
        self._path_label.setStyleSheet("color: #8b949e; font-size: 11px;")
        path_layout.addWidget(self._path_label)

        browse_btn = QPushButton("Browse…")
        browse_btn.setStyleSheet(self._btn_style("#21262d"))
        browse_btn.clicked.connect(self._browse_project)
        path_layout.addWidget(browse_btn)
        layout.addWidget(path_box)

        # ── Output formats ────────────────────────────────────────────────────
        fmt_box = QGroupBox("Output Formats")
        fmt_box.setStyleSheet(self._group_style())
        fmt_layout = QVBoxLayout(fmt_box)

        self._fmt_checks: dict[str, QCheckBox] = {}
        for fmt in _FORMATS:
            cb = QCheckBox(fmt.upper())
            cb.setChecked(fmt in ("toon", "html", "md"))
            cb.setStyleSheet("color: #c9d1d9; font-size: 11px;")
            fmt_layout.addWidget(cb)
            self._fmt_checks[fmt] = cb
        layout.addWidget(fmt_box)

        # ── Analysis options ──────────────────────────────────────────────────
        opts_box = QGroupBox("Options")
        opts_box.setStyleSheet(self._group_style())
        opts_layout = QVBoxLayout(opts_box)

        self._no_cache_cb = QCheckBox("No Cache (full re-analysis)")
        self._no_cache_cb.setStyleSheet("color: #c9d1d9; font-size: 11px;")
        opts_layout.addWidget(self._no_cache_cb)

        self._no_security_cb = QCheckBox("Disable Secret Scan")
        self._no_security_cb.setStyleSheet("color: #c9d1d9; font-size: 11px;")
        opts_layout.addWidget(self._no_security_cb)

        # Instruction file
        instr_label = QLabel("Instruction file:")
        instr_label.setStyleSheet("color: #8b949e; font-size: 11px;")
        opts_layout.addWidget(instr_label)

        instr_row = QHBoxLayout()
        self._instr_edit = QLineEdit()
        self._instr_edit.setPlaceholderText("e.g. AGENTS.md")
        self._instr_edit.setStyleSheet(self._input_style())
        instr_row.addWidget(self._instr_edit)

        instr_browse = QPushButton("…")
        instr_browse.setFixedWidth(30)
        instr_browse.setStyleSheet(self._btn_style("#21262d"))
        instr_browse.clicked.connect(self._browse_instruction)
        instr_row.addWidget(instr_browse)
        opts_layout.addLayout(instr_row)

        # Output dir override
        out_label = QLabel("Output dir (blank = project root):")
        out_label.setStyleSheet("color: #8b949e; font-size: 11px;")
        opts_layout.addWidget(out_label)

        out_row = QHBoxLayout()
        self._out_edit = QLineEdit()
        self._out_edit.setPlaceholderText(".")
        self._out_edit.setStyleSheet(self._input_style())
        out_row.addWidget(self._out_edit)

        out_browse = QPushButton("…")
        out_browse.setFixedWidth(30)
        out_browse.setStyleSheet(self._btn_style("#21262d"))
        out_browse.clicked.connect(self._browse_output_dir)
        out_row.addWidget(out_browse)
        opts_layout.addLayout(out_row)

        layout.addWidget(opts_box)

        # ── Run button ────────────────────────────────────────────────────────
        self._run_btn = QPushButton("Run Analysis")
        self._run_btn.setStyleSheet(self._btn_style("#1f6feb", text_color="#ffffff"))
        self._run_btn.setMinimumHeight(36)
        self._run_btn.clicked.connect(self._on_run_clicked)
        layout.addWidget(self._run_btn)

        self._cancel_btn = QPushButton("Cancel")
        self._cancel_btn.setStyleSheet(self._btn_style("#b62324", text_color="#ffffff"))
        self._cancel_btn.setMinimumHeight(28)
        self._cancel_btn.setEnabled(False)
        self._cancel_btn.hide()
        layout.addWidget(self._cancel_btn)

        layout.addStretch()

    # ── Public API ────────────────────────────────────────────────────────────

    def set_project_path(self, path: Path) -> None:
        self._path_label.setText(str(path))

    def get_project_path(self) -> Path | None:
        text = self._path_label.text()
        if text == "(none selected)":
            return None
        return Path(text)

    def set_running(self, running: bool) -> None:
        self._run_btn.setEnabled(not running)
        self._cancel_btn.setEnabled(running)
        if running:
            self._cancel_btn.show()
        else:
            self._cancel_btn.hide()

    def get_options(self) -> dict[str, Any]:
        selected_fmts = [fmt for fmt, cb in self._fmt_checks.items() if cb.isChecked()]
        return {
            "formats": selected_fmts or ["toon"],
            "no_cache": self._no_cache_cb.isChecked(),
            "no_security": self._no_security_cb.isChecked(),
            "instruction_file": self._instr_edit.text().strip(),
            "output_dir": self._out_edit.text().strip(),
        }

    # ── Slots ─────────────────────────────────────────────────────────────────

    def _browse_project(self) -> None:
        path = QFileDialog.getExistingDirectory(
            self, "Select Project Directory", str(Path.home())
        )
        if path:
            self._path_label.setText(path)

    def _browse_instruction(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Instruction File", str(Path.home()), "All Files (*)"
        )
        if path:
            self._instr_edit.setText(path)

    def _browse_output_dir(self) -> None:
        path = QFileDialog.getExistingDirectory(
            self, "Select Output Directory", str(Path.home())
        )
        if path:
            self._out_edit.setText(path)

    def _on_run_clicked(self) -> None:
        root = self.get_project_path()
        if root is None or not root.is_dir():
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "No Project", "Please select a valid project directory.")
            return
        self.run_requested.emit(root, self.get_options())

    # ── Style helpers ─────────────────────────────────────────────────────────

    @staticmethod
    def _group_style() -> str:
        return (
            "QGroupBox {"
            "  color: #8b949e;"
            "  border: 1px solid #30363d;"
            "  border-radius: 6px;"
            "  margin-top: 6px;"
            "  font-size: 11px;"
            "  padding: 6px;"
            "}"
            "QGroupBox::title {"
            "  subcontrol-origin: margin;"
            "  left: 8px;"
            "  padding: 0 4px;"
            "}"
        )

    @staticmethod
    def _btn_style(bg: str, text_color: str = "#c9d1d9") -> str:
        return (
            f"QPushButton {{"
            f"  background-color: {bg};"
            f"  color: {text_color};"
            f"  border: 1px solid #30363d;"
            f"  border-radius: 4px;"
            f"  padding: 4px 10px;"
            f"  font-size: 11px;"
            f"}}"
            f"QPushButton:hover {{ background-color: #30363d; }}"
            f"QPushButton:disabled {{ color: #484f58; }}"
        )

    @staticmethod
    def _input_style() -> str:
        return (
            "QLineEdit {"
            "  background-color: #0d1117;"
            "  color: #c9d1d9;"
            "  border: 1px solid #30363d;"
            "  border-radius: 4px;"
            "  padding: 3px 6px;"
            "  font-size: 11px;"
            "}"
        )
