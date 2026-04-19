"""Background worker that runs AnalysisEngine on a QThread.

All heavy work happens in `run()` which is invoked by QThread.started.
Signals bridge results back to the GUI thread via Qt's queued connections.
"""

from __future__ import annotations

import logging
import traceback
from pathlib import Path
from typing import Any

from PySide6.QtCore import QObject, Signal


class _QtLogHandler(logging.Handler):
    """Forwards log records to a Qt signal so the GUI log console gets them."""

    def __init__(self, signal: Signal) -> None:  # type: ignore[type-arg]
        super().__init__()
        self._sig = signal

    def emit(self, record: logging.LogRecord) -> None:
        try:
            self._sig.emit(self.format(record))
        except Exception:
            pass


class EngineWorker(QObject):
    """Wraps AnalysisEngine for execution on a background QThread.

    Options dict keys
    -----------------
    no_cache      : bool  — clear cache before analysis
    no_security   : bool  — disable secret scanner
    formats       : list[str]  — e.g. ["toon", "html"]
    output_dir    : str   — override output directory
    instruction_file : str — path to instruction/context file
    """

    # Emitted from the worker thread — Qt delivers them in the GUI thread.
    progress = Signal(int, int)          # (done, total)
    log_line = Signal(str)              # single log message
    analysis_done = Signal(object, object)  # (output_data dict, files_snapshot dict)
    file_written = Signal(str, object)  # (format_name, Path)
    error = Signal(str)                 # error message (may include traceback)
    finished = Signal()                 # always emitted last

    # ── Supported format names ────────────────────────────────────────────────
    ALL_FORMATS: frozenset[str] = frozenset({"toon", "json", "html", "md", "xml", "dsl"})

    def __init__(self, root: Path, options: dict[str, Any], parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._root = root
        self._options = options
        self._cancel = False

    # ── Public ────────────────────────────────────────────────────────────────

    def cancel(self) -> None:
        """Request cancellation. The worker checks this flag in _on_progress."""
        self._cancel = True

    def run(self) -> None:
        """Entry point called by QThread.started. Must not be called directly."""
        # ── Set up logging bridge ─────────────────────────────────────────────
        handler = _QtLogHandler(self.log_line)
        handler.setFormatter(logging.Formatter("%(levelname)s  %(name)s — %(message)s"))
        logger = logging.getLogger("ai-indexer")
        original_propagate = logger.propagate
        logger.propagate = False
        logger.addHandler(handler)

        try:
            self._run_analysis()
        except Exception:
            self.error.emit(traceback.format_exc())
        finally:
            logger.removeHandler(handler)
            logger.propagate = original_propagate
            self.finished.emit()

    # ── Private ───────────────────────────────────────────────────────────────

    def _run_analysis(self) -> None:
        from ai_indexer.core.engine import AnalysisEngine
        from ai_indexer.main import _build_output, _write_outputs
        from ai_indexer.utils.config import load_config

        root = self._root
        opts = self._options
        self._cancel = False

        self.log_line.emit(f"Loading config from {root}")
        config = load_config(root)

        # Apply GUI option overrides onto the config data dict
        if opts.get("no_security"):
            config._d.setdefault("security", {})["enabled"] = False

        out_dir_override = opts.get("output_dir", "").strip()
        if out_dir_override:
            config._d["output_dir"] = out_dir_override

        out_dir = (root / config.output_dir).resolve()
        out_dir.mkdir(parents=True, exist_ok=True)

        self.log_line.emit(f"Output directory: {out_dir}")

        engine = AnalysisEngine(root, config)
        if opts.get("no_cache"):
            engine.cache.clear()
            self.log_line.emit("Cache cleared — full re-analysis")

        self.log_line.emit("Running analysis…")
        try:
            engine.run(on_progress=self._on_progress)
        except InterruptedError:
            self.log_line.emit("Analysis cancelled by user.")
            engine.cache.save()
            return

        self.log_line.emit(f"Analysis complete — {len(engine.files)} files indexed")

        # ── Instruction file ──────────────────────────────────────────────────
        instruction = ""
        instr_file = opts.get("instruction_file", "").strip()
        if not instr_file:
            instr_file = config.instruction_file
        if instr_file:
            instr_path = Path(instr_file)
            if not instr_path.is_absolute():
                instr_path = root / instr_path
            try:
                instruction = instr_path.read_text(encoding="utf-8").strip()
                self.log_line.emit(f"Loaded instruction file: {instr_path}")
            except Exception as exc:
                self.log_line.emit(f"Warning: could not read instruction file: {exc}")

        # ── Build output data ─────────────────────────────────────────────────
        output_data = _build_output(engine, instruction=instruction)

        # ── Write output files ────────────────────────────────────────────────
        selected_fmts: list[str] = list(opts.get("formats", ["toon", "html", "md"]))
        if self.ALL_FORMATS <= set(selected_fmts):
            # All formats selected — use "all" for a single call
            written = _write_outputs(engine, output_data, "all", None, out_dir)
            for fmt_name, path in written:
                self.log_line.emit(f"Written: {path.name}")
                self.file_written.emit(fmt_name, path)
        else:
            for fmt_name in selected_fmts:
                written = _write_outputs(engine, output_data, fmt_name, None, out_dir)
                for f, path in written:
                    self.log_line.emit(f"Written: {path.name}")
                    self.file_written.emit(f, path)

        # ── Build serialisable files snapshot ─────────────────────────────────
        files_snapshot: dict[str, Any] = {
            path: fd.to_dict(compact=False)
            for path, fd in engine.files.items()
        }

        self.analysis_done.emit(output_data, files_snapshot)

    def _on_progress(self, done: int, total: int) -> None:
        """Called by AnalysisEngine on each file processed. Raises on cancel."""
        if self._cancel:
            raise InterruptedError("cancelled by user")
        self.progress.emit(done, total)
