# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

`ai-indexer` is a CLI tool (`ai-indexer`) that analyzes a project directory and generates structured metadata for LLM consumption. It produces dependency graphs, complexity metrics, and prioritized hotspot lists across multiple output formats.

## Development Commands

```bash
# Install with all optional dependencies
pip install -e ".[full,dev]"

# Run the indexer on a directory
ai-indexer [project_dir] [--format toon|json|md|html|all] [--output FILE] [--no-cache] [--mcp] [--audio]

# Linting
ruff check src/

# Type checking
mypy src/

# Tests
pytest
# Run a single test file
pytest tests/path/to/test_file.py
```

## Architecture

The pipeline flows: `main.py` → `AnalysisEngine` → parsers → exporters/MCP server.

### Core (`src/ai_indexer/core/`)
- **`engine.py`** — Orchestrates the full analysis: discovers files (respecting `.gitignore` and `_IGNORE_DIRS`), runs parsers in parallel via `ThreadPoolExecutor`, builds a forward/reverse dependency graph, computes PageRank, and enriches `FileMetadata` with derived v8 metrics (`refactor_effort`, `blast_radius`).
- **`models.py`** — `FileMetadata` dataclass (slots-based for memory efficiency) representing a single file. `ConfidenceValue` wraps a string label with a float confidence. `compute_refactor_effort` and `compute_blast_radius_2hop` are standalone functions used during enrichment.
- **`cache.py`** — `AnalysisCache` persists per-file metadata in `.aicontext_cache_v8.json`, keyed by `path:mtime:size`. Flushes every 50 dirty entries. Use `--no-cache` to bypass it.

### Parsers (`src/ai_indexer/parsers/`)
- **`base.py`** — `ParseResult` dataclass + `BaseParser` ABC. `ParserRegistry` dispatches by file extension.
- **`python.py`** / **`typescript.py`** — Concrete parsers that extract imports, exports, functions, classes, docstrings, and type hints. They return a `ParseResult` with resolved internal dependencies via `ImportResolver`.

### Exporters (`src/ai_indexer/exporters/`)
All inherit from `BaseExporter` (abstract `export(data, path)` method):
- **`toon.py`** — Custom TOON format: a compact YAML-like format using a columnar `@rows` layout for the `files` section to cut ~40–60% of tokens vs JSON.
- **`html.py`** — Interactive HTML report with the full analysis data.

### MCP Server (`src/ai_indexer/mcp/server.py`)
A JSON-RPC 2.0 server over stdio, started with `--mcp`. Supports: `get_dependents`, `search_symbol`, `get_file_summary`, `list_hotspots`, `list_orphans`, `list_by_blast_radius`, `list_refactor_candidates`.

### Audio Tours (`src/ai_indexer/audio_tours/`, `src/ai_indexer/tours/`)
100% offline audio generation: `TourGenerator` builds a `ProjectTour` from the engine output, `ScriptBuilder` converts it to a narration script (with phonetic cleanup for TTS), `LocalNarrator` synthesizes via `pyttsx3`, and `mixer.py` optionally blends background music using `pydub`. Requires `pip install pyttsx3 pydub`.

### Utilities (`src/ai_indexer/utils/`)
- **`config.py`** — Loads `.indexer.yaml` from the project root into `IndexerConfig`. All fields have sane defaults; YAML is optional (requires `pyyaml`).
- **`io.py`** — `safe_read_text` (mmap for files >1 MB), `count_tokens` (tiktoken or len//4 fallback), `ImportResolver`, `GitignoreFilter`, `build_import_resolution_state`.

## Configuration

Place `.indexer.yaml` in the project root to override defaults:

```yaml
exclude_dirs: ["scripts"]
exclude_patterns: ["*.generated.ts"]
criticality_overrides: {"src/core/engine.py": "critical"}
domain_overrides: {"src/legacy/": "backend"}
max_depth: 8          # directory traversal depth
max_workers: 0        # 0 = auto (cpu_count * 2)
output_dir: "."       # where outputs are written
chunk_max_tokens: 800
```

## Output Files

The indexer writes to the project root (or `output_dir`):
- `estrutura_projeto.json` — full analysis as compact JSON
- `estrutura_projeto.toon` — compact TOON format (token-efficient)
- `estrutura_projeto.html` — interactive HTML report
- `estrutura_projeto.md` — Markdown summary with hotspot table
- `.aicontext_cache_v8.json` — incremental analysis cache (not committed)

## Versioning

The version string lives in **two canonical places** — both must be updated together:

1. `src/ai_indexer/__init__.py` — `__version__ = "X.Y.Z"` (and the module docstring on line 1)
2. `pyproject.toml` — `version = "X.Y.Z"` under `[project]`

There is also a hardcoded fallback in `src/ai_indexer/exporters/html.py` (`data.get("version", "X.Y.Z")`) that should be kept in sync.

**Scheme:** `MAJOR.MINOR.PATCH` following [SemVer](https://semver.org/):
- `PATCH` — bug fixes, doc updates, minor tweaks (e.g. `0.0.5` → `0.0.6`)
- `MINOR` — new features, new exporters, new CLI flags (e.g. `0.0.5` → `0.1.0`)
- `MAJOR` — breaking changes to output format or public API (e.g. `0.x.y` → `1.0.0`)

Never change only one of the two canonical files. After bumping, verify with:
```bash
ai-indexer --version
```

## Key Constraints

- Python ≥ 3.11 required; `pyproject.toml` core deps are only `pydantic>=2.0` and `pathspec>=0.11`. Tree-sitter parsers, tiktoken, Jinja2, and PyYAML are all optional (`[full]` extra).
- `ruff` line-length is 100; `mypy` runs in strict mode.
- The engine ignores `.venv`, `node_modules`, `__pycache__`, and other standard build/dependency directories by default — see `_IGNORE_DIRS` in `engine.py:42`.
