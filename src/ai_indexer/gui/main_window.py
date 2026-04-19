"""Main application window — layout, menu bar, and worker lifecycle."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from PySide6.QtCore import Qt, QThread, QUrl
from PySide6.QtGui import QAction, QDesktopServices, QKeySequence
from PySide6.QtWidgets import (
    QFileDialog,
    QLabel,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QSizePolicy,
    QSplitter,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)

from ai_indexer import __version__
from ai_indexer.gui.components.files_table import FilesTable
from ai_indexer.gui.components.hotspots_panel import HotspotsPanel
from ai_indexer.gui.components.log_console import LogConsole
from ai_indexer.gui.components.output_panel import OutputPanel
from ai_indexer.gui.components.project_panel import ProjectPanel
from ai_indexer.gui.components.warnings_panel import WarningsPanel
from ai_indexer.gui.engine_worker import EngineWorker


class MainWindow(QMainWindow):
    """Primary application window."""

    def __init__(self) -> None:
        super().__init__()
        self._worker: EngineWorker | None = None
        self._thread: QThread | None = None
        self._current_root: Path | None = None
        self._last_html: Path | None = None

        self.setWindowTitle(f"AI Indexer  v{__version__}")
        self.resize(1280, 820)
        self.setMinimumSize(900, 600)

        self._build_ui()
        self._build_menu()
        self._build_status_bar()

    # ── Layout ────────────────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)

        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # ── Main horizontal splitter (left panel | right workspace) ───────────
        h_splitter = QSplitter(Qt.Orientation.Horizontal)
        h_splitter.setHandleWidth(1)
        h_splitter.setStyleSheet("QSplitter::handle { background: #30363d; }")

        # Left: project panel
        self._project_panel = ProjectPanel()
        self._project_panel.setMaximumWidth(260)
        self._project_panel.setMinimumWidth(200)
        self._project_panel.run_requested.connect(self.start_analysis)
        h_splitter.addWidget(self._project_panel)

        # Right: vertical splitter (files table + mid row + log)
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)

        # ── Vertical splitter: top (files) / bottom (log) ─────────────────────
        v_splitter = QSplitter(Qt.Orientation.Vertical)
        v_splitter.setHandleWidth(1)
        v_splitter.setStyleSheet("QSplitter::handle { background: #30363d; }")

        # Top part: files table over mid panels
        top_widget = QWidget()
        top_layout = QVBoxLayout(top_widget)
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(0)

        top_v = QSplitter(Qt.Orientation.Vertical)
        top_v.setHandleWidth(1)
        top_v.setStyleSheet("QSplitter::handle { background: #30363d; }")

        self._files_table = FilesTable()
        top_v.addWidget(self._files_table)

        # Mid row: hotspots | warnings | output files
        mid_splitter = QSplitter(Qt.Orientation.Horizontal)
        mid_splitter.setHandleWidth(1)
        mid_splitter.setStyleSheet("QSplitter::handle { background: #30363d; }")

        self._hotspots_panel = HotspotsPanel()
        mid_splitter.addWidget(self._hotspots_panel)

        self._warnings_panel = WarningsPanel()
        mid_splitter.addWidget(self._warnings_panel)

        self._output_panel = OutputPanel()
        self._output_panel.setMaximumWidth(300)
        mid_splitter.addWidget(self._output_panel)
        mid_splitter.setSizes([300, 350, 250])

        top_v.addWidget(mid_splitter)
        top_v.setSizes([450, 250])
        top_layout.addWidget(top_v)
        v_splitter.addWidget(top_widget)

        # Bottom: log console
        self._log_console = LogConsole()
        self._log_console.setMaximumHeight(200)
        self._log_console.setMinimumHeight(60)
        v_splitter.addWidget(self._log_console)
        v_splitter.setSizes([600, 150])

        right_layout.addWidget(v_splitter)
        h_splitter.addWidget(right_widget)
        h_splitter.setSizes([230, 1050])

        root_layout.addWidget(h_splitter)

    def _build_menu(self) -> None:
        menu_bar = self.menuBar()

        # ── App ───────────────────────────────────────────────────────────────
        app_menu = menu_bar.addMenu("App")
        about_act = QAction("About AI Indexer", self)
        about_act.triggered.connect(self._show_about)
        app_menu.addAction(about_act)
        app_menu.addSeparator()
        quit_act = QAction("Quit", self)
        quit_act.setShortcut(QKeySequence.StandardKey.Quit)
        quit_act.triggered.connect(self.close)
        app_menu.addAction(quit_act)

        # ── File ──────────────────────────────────────────────────────────────
        file_menu = menu_bar.addMenu("File")
        open_act = QAction("Open Project…", self)
        open_act.setShortcut(QKeySequence("Ctrl+O"))
        open_act.triggered.connect(self._menu_open_project)
        file_menu.addAction(open_act)

        open_out_act = QAction("Open Output Directory…", self)
        open_out_act.triggered.connect(self._menu_open_output_dir)
        file_menu.addAction(open_out_act)

        # ── Settings ─────────────────────────────────────────────────────────
        settings_menu = menu_bar.addMenu("Settings")

        self._cache_act = QAction("Use Cache", self)
        self._cache_act.setCheckable(True)
        self._cache_act.setChecked(True)
        self._cache_act.triggered.connect(self._toggle_cache)
        settings_menu.addAction(self._cache_act)

        self._security_act = QAction("Enable Security Scan", self)
        self._security_act.setCheckable(True)
        self._security_act.setChecked(True)
        self._security_act.triggered.connect(self._toggle_security)
        settings_menu.addAction(self._security_act)

        settings_menu.addSeparator()
        instr_act = QAction("Select Instruction File…", self)
        instr_act.triggered.connect(self._select_instruction_file)
        settings_menu.addAction(instr_act)

        # ── Actions ───────────────────────────────────────────────────────────
        actions_menu = menu_bar.addMenu("Actions")

        run_act = QAction("Run Analysis", self)
        run_act.setShortcut(QKeySequence("Ctrl+R"))
        run_act.triggered.connect(self._menu_run)
        actions_menu.addAction(run_act)

        cancel_act = QAction("Cancel", self)
        cancel_act.setShortcut(QKeySequence("Ctrl+."))
        cancel_act.triggered.connect(self._menu_cancel)
        actions_menu.addAction(cancel_act)

        actions_menu.addSeparator()

        html_act = QAction("Open HTML Report", self)
        html_act.setShortcut(QKeySequence("Ctrl+Shift+H"))
        html_act.triggered.connect(self._open_html_report)
        actions_menu.addAction(html_act)

        reveal_act = QAction("Reveal Project in Finder", self)
        reveal_act.triggered.connect(self._reveal_project)
        actions_menu.addAction(reveal_act)

    def _build_status_bar(self) -> None:
        status = QStatusBar()
        self.setStatusBar(status)

        self._progress_bar = QProgressBar()
        self._progress_bar.setMaximumWidth(200)
        self._progress_bar.setMinimumWidth(120)
        self._progress_bar.setValue(0)
        self._progress_bar.setTextVisible(True)
        self._progress_bar.setVisible(False)
        self._progress_bar.setStyleSheet(
            "QProgressBar {"
            "  border: 1px solid #30363d;"
            "  border-radius: 3px;"
            "  background-color: #161b22;"
            "  color: #c9d1d9;"
            "  text-align: center;"
            "  font-size: 10px;"
            "}"
            "QProgressBar::chunk { background-color: #1f6feb; border-radius: 2px; }"
        )
        status.addPermanentWidget(self._progress_bar)

        self._status_label = QLabel("Ready")
        self._status_label.setStyleSheet("color: #8b949e; font-size: 11px; padding: 0 8px;")
        status.addWidget(self._status_label)

    # ── Analysis lifecycle ────────────────────────────────────────────────────

    def start_analysis(self, root: Path, options: dict[str, Any]) -> None:
        """Launch a background EngineWorker. Called from ProjectPanel signal."""
        if self._thread and self._thread.isRunning():
            QMessageBox.warning(self, "Busy", "Analysis already running. Cancel it first.")
            return

        self._current_root = root
        self._log_console.clear()
        self._output_panel.clear()
        self._files_table.clear()
        self._hotspots_panel.clear()
        self._warnings_panel.clear()
        self._last_html = None

        self._set_running(True)
        self._status_label.setText(f"Analysing {root.name}…")
        self._progress_bar.setVisible(True)
        self._progress_bar.setRange(0, 0)  # indeterminate until we know file count

        self._thread = QThread(self)
        self._worker = EngineWorker(root, options)
        self._worker.moveToThread(self._thread)

        # Wire signals
        self._thread.started.connect(self._worker.run)
        self._worker.progress.connect(self._on_progress)
        self._worker.log_line.connect(self._log_console.append_line)
        self._worker.analysis_done.connect(self._on_analysis_done)
        self._worker.file_written.connect(self._on_file_written)
        self._worker.error.connect(self._on_error)
        self._worker.finished.connect(self._on_worker_finished)
        self._worker.finished.connect(self._thread.quit)
        self._worker.finished.connect(self._worker.deleteLater)
        self._thread.finished.connect(self._thread.deleteLater)

        # Wire cancel button
        self._project_panel._cancel_btn.clicked.connect(self._menu_cancel)

        self._thread.start()

    def _set_running(self, running: bool) -> None:
        self._project_panel.set_running(running)

    # ── Worker signal slots ───────────────────────────────────────────────────

    def _on_progress(self, done: int, total: int) -> None:
        if total == 0:
            return
        if done == 0:
            # Initial scan complete — now we know total
            self._progress_bar.setRange(0, total)
            self._progress_bar.setValue(0)
        else:
            self._progress_bar.setRange(0, total)
            self._progress_bar.setValue(done)
        pct = int(done / total * 100) if total else 0
        self._status_label.setText(f"Analysing… {done}/{total} ({pct}%)")

    def _on_analysis_done(
        self, output_data: dict[str, Any], files_snapshot: dict[str, Any]
    ) -> None:
        root = self._current_root or Path(".")
        self._files_table.populate(files_snapshot, root)
        self._hotspots_panel.populate(output_data.get("hotspots", []))
        self._warnings_panel.populate(files_snapshot)
        n_files = output_data.get("stats", {}).get("total_files", 0)
        self._status_label.setText(f"Done — {n_files} files indexed")

    def _on_file_written(self, fmt: str, path: object) -> None:
        p = Path(str(path))
        self._output_panel.add_file(fmt, p)
        if fmt == "html":
            self._last_html = p

    def _on_error(self, msg: str) -> None:
        self._log_console.append_line(f"\n=== ERROR ===\n{msg}")
        self._status_label.setText("Error — see log")
        QMessageBox.critical(self, "Analysis Error", msg[:500])

    def _on_worker_finished(self) -> None:
        self._set_running(False)
        self._progress_bar.setVisible(False)
        self._worker = None
        self._thread = None

    # ── Menu actions ──────────────────────────────────────────────────────────

    def _menu_open_project(self) -> None:
        path = QFileDialog.getExistingDirectory(
            self, "Open Project Directory", str(Path.home())
        )
        if path:
            self._project_panel.set_project_path(Path(path))

    def _menu_open_output_dir(self) -> None:
        root = self._current_root
        if root:
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(root)))
        else:
            QMessageBox.information(self, "No Project", "Run an analysis first.")

    def _toggle_cache(self, checked: bool) -> None:
        # Sync with the project panel checkbox
        self._project_panel._no_cache_cb.setChecked(not checked)

    def _toggle_security(self, checked: bool) -> None:
        self._project_panel._no_security_cb.setChecked(not checked)

    def _select_instruction_file(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Instruction File", str(Path.home()), "All Files (*)"
        )
        if path:
            self._project_panel._instr_edit.setText(path)

    def _menu_run(self) -> None:
        root = self._project_panel.get_project_path()
        if root is None:
            self._menu_open_project()
            return
        opts = self._project_panel.get_options()
        self.start_analysis(root, opts)

    def _menu_cancel(self) -> None:
        if self._worker:
            self._worker.cancel()
            self._status_label.setText("Cancelling…")

    def _open_html_report(self) -> None:
        if self._last_html and self._last_html.exists():
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(self._last_html)))
        else:
            QMessageBox.information(self, "No HTML Report", "Run analysis with HTML format first.")

    def _reveal_project(self) -> None:
        root = self._current_root
        if root and root.exists():
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(root)))
        else:
            QMessageBox.information(self, "No Project", "Select a project directory first.")

    def _show_about(self) -> None:
        QMessageBox.about(
            self,
            "About AI Indexer",
            f"<b>AI Context Indexer</b> v{__version__}<br><br>"
            "Analyzes project directories and generates structured metadata "
            "for LLM consumption.<br><br>"
            "Dependency graphs · Complexity metrics · Hotspot detection<br>"
            "Security scanning · Multiple output formats",
        )
