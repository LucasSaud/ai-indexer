# ai-indexer DSL 0.0.7 | ai-indexer | 32 files | 3 domains | 2026-04-17
# Hotspots: src/ai_indexer/main.py  src/ai_indexer/mcp/server.py  src/ai_indexer/core/engine.py

[MOD:u/critical] src/ai_indexer/main.py
  [DOC] entrypoint – CLI entrypoint for AI Context Indexer.
  [CLS] _Formatter
  [FN] _build_parser -> argparse.ArgumentParser p.add_argument p.add_argument_group out_group.add_argument
  [FN] _build_output -> isoformat _detect_modules len sum
  [FN] _detect_modules -> defaultdict values dict _Path
  [FN] _write_outputs -> export log.info written.append path.write_text
  [FN] _write_md -> data.get strftime lines.append path.write_text
  [DEP] src/ai_indexer/exporters/html.py  src/ai_indexer/audio_tours/narrator.py  src/ai_indexer/audio_tours/mixer.py  src/ai_indexer/utils/ui.py

[MOD:u/critical] src/ai_indexer/mcp/server.py
  [DOC] entrypoint – MCP (Model Context Protocol) server — JSON-RPC 2.0 over stdio.
  [CLS] MCPServer
  [FN] get_dependents -> list get
  [FN] search_symbol -> symbol_name.lower items caps.get hits.append
  [FN] get_file_summary -> get round items
  [FN] list_hotspots -> round sorted values
  [FN] __init__
  [DEP] src/ai_indexer/core/models.py  src/ai_indexer/exporters/dsl.py

[MOD:u/critical] src/ai_indexer/core/engine.py
  [DOC] core – Analysis engine — orchestrates parsing, graph building, metric enrichment
  [CLS] FileMetaDict AnalysisEngine
  [FN] __init__ -> AnalysisCache defaultdict ParserRegistry _register_default_parsers
  [FN] _register_default_parsers -> register PythonParser TypeScriptParser
  [FN] run -> time.time log.info _collect_files _build_file_index
  [FN] _update_files_and_cache -> save set _meta_to_model
  [FN] _post_process -> _build_graph _enrich_graph_metrics _compute_v8_metrics _apply_arch_rules
  [DEP] src/ai_indexer/exporters/base.py  src/ai_indexer/utils/security.py  src/ai_indexer/core/cache.py  src/ai_indexer/utils/io.py

[MOD:u/critical] src/ai_indexer/gui/app.py
  [DOC] entrypoint – QApplication entry point — palette, Fusion theme, and main() for th
  [FN] build_dark_palette -> QPalette palette.setColor QColor
  [FN] main -> QApplication.setHighDpiScaleFactorRoundingPolicy QApplication app.setApplicationName app.setApplicationVersion
  [DEP] src/ai_indexer/gui/main_window.py

[MOD:u/critical] src/ai_indexer/gui/main_window.py
  [DOC] entrypoint – Main application window — layout, menu bar, and worker lifecycle.
  [CLS] MainWindow
  [FN] __init__ -> __init__ setWindowTitle resize setMinimumSize
  [FN] _build_ui -> QWidget setCentralWidget QVBoxLayout root_layout.setContentsMargins
  [FN] _build_menu -> menuBar menu_bar.addMenu QAction connect
  [FN] _build_status_bar -> QStatusBar setStatusBar QProgressBar setMaximumWidth
  [FN] start_analysis -> clear _set_running setText setVisible
  [DEP] src/ai_indexer/gui/components/output_panel.py  src/ai_indexer/gui/components/log_console.py  src/ai_indexer/gui/engine_worker.py  src/ai_indexer/gui/components/hotspots_panel.py

[MOD:i/critical] src/ai_indexer/core/cache.py
  [DOC] core – Incremental analysis cache.
  [CLS] AnalysisCache
  [FN] __init__ -> _load
  [FN] _load -> exists json.loads log.debug read_text
  [FN] save -> with_suffix temp_path.write_text os.replace json.dumps
  [FN] _key -> path.stat str path.resolve
  [FN] get -> get _key

[MOD:u/critical] src/ai_indexer/core/models.py
  [DOC] core – Core data models for the AI Context Indexer.
  [CLS] ConfidenceValue FileMetadata
  [FN] compute_refactor_effort -> abs math.log
  [FN] compute_blast_radius_2hop -> set reverse_graph.get len visited.add
  [FN] to_dict -> to_dict round items

[MOD:u/critical] src/ai_indexer/mcp/http_server.py
  [DOC] entrypoint – Minimal stdlib HTTP server that exposes MCP query methods as REST e
  [CLS] _Handler HttpMcpServer
  [FN] log_message -> log.debug
  [FN] do_GET -> urlparse parse_qs rstrip _send
  [FN] _send -> encode send_response send_header end_headers
  [FN] __init__ -> MCPServer
  [FN] serve -> HTTPServer log.info print server.serve_forever
  [DEP] src/ai_indexer/core/models.py  src/ai_indexer/mcp/server.py

[MOD:a/supporting] src/ai_indexer/gui/engine_worker.py
  [DOC] worker – Background worker that runs AnalysisEngine on a QThread.
  [CLS] _QtLogHandler EngineWorker
  [FN] __init__ -> __init__ super
  [FN] emit -> emit format
  [FN] run -> _QtLogHandler handler.setFormatter logging.getLogger logger.addHandler
  [FN] _run_analysis -> emit load_config opts.get strip
  [FN] cancel
  [DEP] src/ai_indexer/core/engine.py  src/ai_indexer/utils/config.py  src/ai_indexer/main.py

[MOD:u/critical] src/ai_indexer/parsers/typescript.py
  [DOC] types – TypeScript / JavaScript language parser.
  [CLS] TypeScriptParser
  [FN] parse -> ParseResult bool _RE_JS_DYN_IMPORT.finditer sorted
  [FN] _parse_tree_sitter -> lower parser.parse _walk_tree _parse_regex
  [FN] _walk_tree -> node.child_by_field_name _walk_tree decode append
  [FN] _extract_jsdoc -> decode text.startswith text.split strip
  [FN] _make_parser
  [DEP] src/ai_indexer/utils/io.py  src/ai_indexer/exporters/base.py

[MOD:p/supporting] src/ai_indexer/gui/components/files_table.py
  [DOC] component – Files table — sortable QTableWidget showing FileMetadata for every f
  [CLS] FilesTable
  [FN] __init__ -> __init__ _build_ui super
  [FN] _build_ui -> QVBoxLayout layout.setContentsMargins layout.setSpacing QLabel
  [FN] populate -> setSortingEnabled setRowCount sorted enumerate
  [FN] clear -> setRowCount setText
  [FN] _extract_values -> meta.get len str isinstance

[MOD:p/supporting] src/ai_indexer/gui/components/output_panel.py
  [DOC] component – Output panel — lists written output files with open/reveal actions.
  [CLS] OutputPanel
  [FN] __init__ -> __init__ _build_ui super
  [FN] _build_ui -> QVBoxLayout layout.setContentsMargins layout.setSpacing QLabel
  [FN] add_file -> QListWidgetItem item.setForeground item.setData item.setToolTip
  [FN] clear -> clear
  [FN] _show_context_menu -> itemAt Path QMenu menu.addAction

[MOD:p/supporting] src/ai_indexer/gui/components/project_panel.py
  [DOC] component – Project panel — path selector, format checkboxes, and Run button.
  [CLS] ProjectPanel
  [FN] __init__ -> __init__ _build_ui super
  [FN] _build_ui -> QVBoxLayout layout.setContentsMargins layout.setSpacing layout.setAlignment
  [FN] set_project_path -> setText str
  [FN] get_project_path -> text Path
  [FN] set_running -> setEnabled show hide

[MOD:u/supporting] src/ai_indexer/utils/io.py
  [DOC] util – I/O utilities: safe file reading (mmap for large files), token counting,
  [CLS] ImportResolver GitignoreFilter
  [FN] count_tokens -> len _TOKEN_COUNTER.encode
  [FN] safe_read_text -> path.read_text path.stat open mmap.mmap
  [FN] build_import_resolution_state -> tsconfig_path.exists pkg_path.exists bunfig_path.exists set
  [FN] __init__ -> gi.exists splitlines from_lines raw.strip
  [FN] resolve_import -> strip sorted specifier.startswith _resolve_bare

[MOD:u/supporting] src/ai_indexer/exporters/dsl.py
  [DOC] module – DSL (Domain-Specific Language) exporter.
  [CLS] DslExporter
  [FN] export -> output_path.write_text _render
  [FN] render_file -> hasattr _render_block fd.to_dict dict
  [FN] _render -> data.get strftime stats.get join
  [FN] _norm -> dict fd.get get
  [FN] _render_block -> strip caps.get join fd.get
  [DEP] src/ai_indexer/exporters/base.py

[MOD:u/supporting] src/ai_indexer/exporters/html.py
  [DOC] module – HTML dashboard exporter.
  [CLS] HtmlExporter
  [FN] export -> _build_context _render output_path.write_text log.info
  [FN] _build_context -> data.get strftime files.items set
  [FN] _render -> _render_inline exists read_text Environment
  [FN] _render_inline -> join str replace h.get
  [FN] stat_card
  [DEP] src/ai_indexer/exporters/base.py

[MOD:u/supporting] src/ai_indexer/exporters/toon.py
  [DOC] module – TOON format exporter.
  [CLS] ToonExporter
  [FN] export -> output_path.write_text _render
  [FN] _render -> parts.append items _render_narrative _render_files_columnar
  [FN] _render_narrative -> data.get stats.get sum lines.append
  [FN] _render_files_columnar -> lines.append files.items join _extract_row
  [FN] _extract_row -> fd.get ft.get d.get
  [DEP] src/ai_indexer/exporters/base.py

[MOD:u/supporting] src/ai_indexer/exporters/xml_exporter.py
  [DOC] port – XML output exporter.
  [CLS] XmlExporter
  [FN] _sub -> ET.SubElement
  [FN] export -> ET.Element data.get ET.SubElement sorted
  [DEP] src/ai_indexer/exporters/base.py

[MOD:u/supporting] src/ai_indexer/parsers/python.py
  [DOC] module – Python language parser (AST-primary, regex fallback).
  [CLS] PythonParser
  [FN] parse -> ParseResult bool ast.parse _walk_ast
  [FN] _walk_ast -> ast.get_docstring set ast.walk sorted
  [FN] _collect_calls -> ast.walk isinstance list dict.fromkeys
  [FN] chunk -> ast.parse ast.iter_child_nodes ast.unparse count_tokens
  [DEP] src/ai_indexer/utils/io.py  src/ai_indexer/exporters/base.py

[MOD:u/supporting] src/ai_indexer/tours/generator.py
  [DOC] module – Tour generator – builds a structured narration tour from AnalysisEngine
  [CLS] TourStep ProjectTour TourGenerator
  [FN] generate_overview_tour -> ProjectTour sorted set files.values
  [FN] __init__
  [DEP] src/ai_indexer/core/engine.py

[MOD:u/supporting] src/ai_indexer/utils/config.py
  [DOC] util – YAML configuration loader for .indexer.yaml project overrides.
  [CLS] IndexerConfig
  [FN] load_config -> config_path.exists IndexerConfig log.warning log.info
  [FN] exclude_dirs -> get
  [FN] exclude_patterns -> get
  [FN] extra_text_filenames -> get
  [FN] __init__

[MOD:u/supporting] src/ai_indexer/utils/ui.py
  [DOC] util – Terminal UI for ai-indexer.
  [CLS] AnalysisUI
  [FN] _file_size -> path.stat
  [FN] __init__ -> isatty Console
  [FN] header -> time.time print
  [FN] on_progress -> Progress start add_task SpinnerColumn
  [FN] active

[MOD:u/supporting] src/ai_indexer/parsers/base.py
  [DOC] module – Abstract base class for language parsers.
  [CLS] ParseResult BaseParser ParserRegistry
  [FN] parse -> get ParseResult parser.parse len
  [FN] can_handle -> lower
  [FN] chunk -> src.splitlines count_tokens chunks.append current.append
  [FN] register -> append
  [FN] __init__
  [DEP] src/ai_indexer/utils/io.py

[MOD:u/supporting] src/ai_indexer/exporters/base.py
  [DOC] module – Abstract base exporter.
  [CLS] BaseExporter
  [FN] export

[MOD:p/supporting] src/ai_indexer/gui/components/hotspots_panel.py
  [DOC] component – Hotspots panel — top-N files by priority score.
  [CLS] HotspotsPanel
  [FN] __init__ -> __init__ _build_ui super
  [FN] _build_ui -> QVBoxLayout layout.setContentsMargins layout.setSpacing QLabel
  [FN] populate -> clear enumerate setText entry.get
  [FN] clear -> clear setText

[MOD:p/supporting] src/ai_indexer/gui/components/log_console.py
  [DOC] component – Log console — streaming read-only QPlainTextEdit for engine output.
  [CLS] LogConsole
  [FN] __init__ -> __init__ _build_ui super
  [FN] _build_ui -> QVBoxLayout layout.setContentsMargins layout.setSpacing QLabel
  [FN] append_line -> appendPlainText textCursor cursor.movePosition setTextCursor
  [FN] clear -> clear

[MOD:p/supporting] src/ai_indexer/gui/components/warnings_panel.py
  [DOC] component – Warnings panel — architectural and security warnings tree.
  [CLS] WarningsPanel
  [FN] __init__ -> __init__ _build_ui super
  [FN] _build_ui -> QVBoxLayout layout.setContentsMargins layout.setSpacing QLabel
  [FN] populate -> clear QTreeWidgetItem arch_root.setForeground arch_root.setExpanded
  [FN] clear -> clear setText

[MOD:u/supporting] src/ai_indexer/audio_tours/mixer.py
  [DOC] module for ai
  [FN] finalize_audio -> wav_path.exists shutil.which AudioSegment.from_wav combined.export

[MOD:u/supporting] src/ai_indexer/audio_tours/narrator.py
  [DOC] module for ai
  [CLS] LocalNarrator
  [FN] __init__ -> pyttsx3.init setProperty
  [FN] list_voices -> getProperty enumerate print
  [FN] synthesize -> getProperty output_path.with_suffix save_to_file runAndWait

[MOD:u/supporting] src/ai_indexer/audio_tours/script_builder.py
  [DOC] builder for ai
  [CLS] ScriptBuilder
  [FN] _clean_text -> items re.sub text.replace
  [FN] build_full_script -> parts.append sorted join _clean_text
  [FN] __init__

[MOD:u/supporting] src/ai_indexer/utils/git_context.py
  [DOC] util – Git context helpers: recent logs, diffs, and change-frequency data.
  [FN] _run -> subprocess.run strip log.debug str
  [FN] is_git_repo -> _run
  [FN] get_recent_logs -> _run raw.splitlines line.split len
  [FN] get_staged_diff -> _run
  [FN] get_file_change_counts -> _run raw.splitlines line.strip counts.get

[MOD:u/supporting] src/ai_indexer/utils/security.py
  [DOC] util – Secret / credential scanner.
  [CLS] _Pattern
  [FN] scan_secrets -> set src.splitlines enumerate lower
