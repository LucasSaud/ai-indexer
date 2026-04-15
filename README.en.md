# ai-indexer

> Analyze a software project and generate structured metadata optimized for LLM consumption.

[![Python](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/)
[![Version](https://img.shields.io/badge/version-0.0.5-green)](https://github.com/LucasSaud/ai-indexer)
[![License](https://img.shields.io/badge/license-MIT-lightgrey)](LICENSE)

**[Versão em Português → README.md](README.md)**

---

## What it is

`ai-indexer` is a command-line tool that scans a project directory, analyzes the source code (Python, TypeScript, JavaScript, and more), builds a dependency graph, and generates compact output files ready to be pasted directly into an LLM context window (Claude, GPT-4, Gemini, etc.).

What the indexer produces for each file:

- **Domain and type** auto-detected (`auth`, `database`, `ui`, `api`, `billing`…)
- **Criticality** (`critical`, `infra`, `config`, `supporting`)
- **Priority score** based on PageRank, fan-in, complexity, and entrypoints
- **Refactor effort** — estimated refactoring cost (lines × complexity × coupling)
- **Blast radius** — how many files would be impacted by a change (2 hops in the graph)
- **Architectural warnings** — dependency cycles, orphan files, excessive coupling
- **Secret detection** — AWS keys, GitHub tokens, Stripe keys, JWTs, hardcoded passwords, and more
- **Functions, classes, and exports** extracted from the AST
- **Docstrings and type hints**
- **Git context** — commit history, diff stat, per-file change frequency

---

## Installation

### Basic installation (no optional dependencies)

```bash
pip install ai-indexer
```

### Full installation (recommended)

Includes tree-sitter for accurate TypeScript/JS parsing, tiktoken for token counting, Jinja2 for HTML templates, and PyYAML for `.indexer.yaml` support:

```bash
pip install "ai-indexer[full]"
```

### Development installation

```bash
git clone https://github.com/LucasSaud/ai-indexer
cd ai-indexer
pip install -e ".[full,dev]"
```

### Optional dependencies by feature

| Feature | Required packages |
|---|---|
| Accurate TS/JS parsing | `tree-sitter tree-sitter-typescript tree-sitter-javascript` |
| Precise token counting | `tiktoken` |
| HTML templates (Jinja2) | `jinja2` |
| `.indexer.yaml` config file | `pyyaml` |
| Audio tour (offline TTS) | `pyttsx3 pydub` |
| Background music mixing | `pydub` + `ffmpeg` installed on the system |

---

## Quick Start

```bash
# Index current directory and generate all output formats
ai-indexer

# Index a specific project
ai-indexer ~/projects/my-app

# Generate only the XML file (best for pasting into Claude)
ai-indexer --format xml ~/projects/my-app

# Generate only TOON (most token-efficient)
ai-indexer --format toon --output context.toon ~/projects/my-app
```

---

## Usage

```
ai-indexer [PROJECT_DIR] [options]
```

If `PROJECT_DIR` is not specified, the current directory is used. If the project has a `src/` folder at its root, analysis is automatically restricted to that subtree.

### Arguments

#### Positional

| Argument | Description |
|---|---|
| `PROJECT_DIR` | Root directory of the project to analyze. Defaults to the current directory. |

#### Output

| Flag | Default | Description |
|---|---|---|
| `--format, -f` | `all` | Output format: `toon`, `json`, `md`, `html`, `xml`, or `all` |
| `--output, -o FILE` | — | Override the output file path (single `--format` mode only) |

#### Content enrichment

| Flag | Description |
|---|---|
| `--instruction-file FILE` | Text/Markdown file whose content is injected as `instruction` in all outputs. In XML it becomes the first `<instruction>` element, which Claude reads as a context directive. |

#### Analysis control

| Flag | Description |
|---|---|
| `--no-cache` | Ignore the incremental cache and re-analyze all files from scratch |
| `--no-security` | Disable the secret/credential scanner |

#### Integrations

| Flag | Description |
|---|---|
| `--mcp` | After indexing, start a JSON-RPC 2.0 MCP server on stdio for IDE plugins and AI agents |

#### Audio tour

| Flag | Default | Description |
|---|---|---|
| `--audio` | — | Generate a narrated audio tour of the codebase using offline system TTS |
| `--audio-rate WPM` | `160` | Speech rate in words per minute |
| `--bg-music FILE` | — | Background music file (MP3/WAV) mixed under the narration |

#### Miscellaneous

| Flag | Description |
|---|---|
| `--verbose, -v` | Enable DEBUG-level logging to stderr |
| `--version` | Display version and exit |
| `--help, -h` | Display full help and exit |

---

## Output Formats

### `toon` — TOON Format (most token-efficient)

A compact proprietary format with a columnar `@rows` layout. Reduces ~40–60% of tokens compared to equivalent JSON. Ideal for pasting directly into an LLM context window.

```bash
ai-indexer --format toon --output context.toon .
```

### `json` — Full JSON

Minified JSON with all metadata: dependency graph, PageRank, v8 metrics, docstrings, type hints, code chunks, and more.

```bash
ai-indexer --format json .
```

### `html` — Interactive 3D Dashboard

Generates a standalone HTML file with a 3D nebula visualizer (Three.js) and a responsive (mobile-first) dashboard. Opens in the browser without a server.

- **Nebula view**: 3D dependency graph with orbit controls, zoom, clickable nodes
- **Dashboard view**: hotspot table, modules, architectural warnings, statistics

```bash
ai-indexer --format html .
open estrutura_projeto.html
```

### `md` — Markdown

Markdown summary with a hotspot table and warnings list. Useful for documentation or PR descriptions.

```bash
ai-indexer --format md .
```

### `xml` — Structured XML (recommended for Claude)

Structured XML format, recommended by Anthropic for use with Claude. Tags make document structure unambiguous and easy for LLMs to parse.

```xml
<?xml version='1.0' encoding='utf-8'?>
<ai_index version="0.0.5" project="my-app" generated_at="...">
  <instruction>You are analyzing a Python/FastAPI e-commerce app...</instruction>
  <file_summary total_files="120" critical="8" domains="6" entrypoints="3"/>
  <hotspots>
    <file path="src/core/engine.py" priority="71" criticality="critical" .../>
  </hotspots>
  <files>
    <file path="src/auth/login.py" criticality="critical" domain="auth" ...>
      <capabilities>
        <functions>authenticate, refresh_token, logout</functions>
      </capabilities>
      <warnings>
        <warning>Possible secret detected: Hardcoded password (line 42)</warning>
      </warnings>
    </file>
  </files>
  <git_context>
    <recent_commits>...</recent_commits>
  </git_context>
</ai_index>
```

```bash
ai-indexer --format xml .
```

---

## Generated Files

All written to the project directory (or the configured `output_dir`):

| File | Description |
|---|---|
| `estrutura_projeto.json` | Full analysis as compact JSON |
| `estrutura_projeto.toon` | Token-efficient TOON format |
| `estrutura_projeto.html` | Interactive dashboard with 3D nebula |
| `estrutura_projeto.md` | Markdown summary |
| `estrutura_projeto.xml` | Structured XML for LLMs |
| `.aicontext_cache_v8.json` | Incremental per-file cache (do not commit) |

---

## Configuration

Create an `.indexer.yaml` file at the project root to override defaults. All fields are optional. Requires `pip install pyyaml`.

```yaml
# ── File selection ────────────────────────────────────────────────────────────

# Directory names to skip (at any depth in the tree)
exclude_dirs: ["scripts", "legacy", "migrations"]

# Glob patterns of files to skip
exclude_patterns: ["*.generated.ts", "*.min.js", "*_pb2.py"]

# Whitelist: if set, only files matching these patterns will be indexed.
# Leave empty to include everything.
include_patterns:
  - "src/**/*.py"
  - "src/**/*.ts"

# ── Analysis ──────────────────────────────────────────────────────────────────

# Maximum directory traversal depth
max_depth: 8

# Number of parallel workers (0 = auto: cpu_count × 2)
max_workers: 0

# Maximum tokens per code chunk
chunk_max_tokens: 800

# ── Output ────────────────────────────────────────────────────────────────────

# Directory where output files are written
output_dir: "."

# Default formats when using --format all
output_formats: ["toon", "html", "md", "xml"]

# ── Manual overrides ──────────────────────────────────────────────────────────

# Force criticality for specific files
criticality_overrides:
  "src/core/engine.py": "critical"
  "src/auth/middleware.py": "critical"

# Force domain for files or folders
domain_overrides:
  "src/legacy/": "backend"
  "src/old_api.py": "api"

# ── Instruction injected into all outputs ─────────────────────────────────────

# Equivalent to --instruction-file in the CLI
instruction_file: "AGENTS.md"

# ── Security ──────────────────────────────────────────────────────────────────

security:
  enabled: true   # false to disable secret detection

# ── Git context (disabled by default) ────────────────────────────────────────

git:
  include_logs: true       # include recent commit log
  logs_count: 10           # number of commits to include
  include_diffs: false     # include HEAD diff stat
  sort_by_changes: false   # collect per-file change frequency
  sort_max_commits: 100    # how many commits to look back for frequency
```

---

## Metrics Explained

### Priority Score

A 0–100 score combining:
- **PageRank** in the dependency graph (heavily imported files score higher)
- **Fan-in** (how many files depend on this one)
- **Estimated cyclomatic complexity**
- **Criticality** (bonus for `critical` and `infra`)
- **Entrypoint** (bonus for files that are application entry points)

### Refactor Effort

Estimated refactoring cost in "effort units". Combines:
- Lines of code
- Number of functions and classes
- Output coupling (fan-out)
- Code complexity

Useful for prioritizing technical debt: files with high `refactor_effort` AND high `criticality` are the most risky.

### Blast Radius

How many files would potentially be impacted by a change to this file, considering 2 hops in the reverse dependency graph.

A high blast radius doesn't mean the file is poorly written — it means changes to it should be made carefully and tested thoroughly.

### Criticality

| Level | Description |
|---|---|
| `critical` | Application core — a failure here breaks everything |
| `infra` | Infrastructure: database, authentication, cache |
| `config` | Configuration and bootstrapping |
| `supporting` | Utilities, helpers, support files |

### Fan-in / Fan-out

- **Fan-in**: number of files that import this file
- **Fan-out**: number of files this file imports

High fan-in = heavily depended-upon file = changes are risky.
High fan-out = highly coupled file = hard to test in isolation.

---

## Secret Detection

The indexer automatically scans all files for credential patterns. Findings appear as `warnings` in all output formats.

Detected patterns:
- AWS access keys (`AKIA...`)
- GitHub tokens (`ghp_...`, `github_pat_...`)
- GitLab tokens (`glpat-...`)
- Private key headers (`-----BEGIN ... PRIVATE KEY-----`)
- Stripe keys (`sk_live_...`, `sk_test_...`)
- Slack tokens (`xox...`)
- JWTs (`eyJ...`)
- Database connection URLs with embedded credentials
- Hardcoded passwords (`password = "..."`, `api_key = "..."`)
- Google API keys (`AIza...`)
- SendGrid, Heroku, npm auth tokens

To disable:
```bash
ai-indexer --no-security
```
Or in `.indexer.yaml`:
```yaml
security:
  enabled: false
```

---

## Instruction Injection

Inject a text file into all outputs as a context directive for the LLM:

```bash
ai-indexer --instruction-file AGENTS.md --format xml
```

The file content appears:
- In JSON: as the `"instruction"` key at the root of the object
- In XML: as the `<instruction>` element, the first child of `<ai_index>`
- In TOON: as the `instruction:` field in the header

Example `AGENTS.md`:
```markdown
You are analyzing a Python/FastAPI e-commerce application.
The payment module (src/billing/) is critical — never suggest structural
changes to it without a full impact analysis.
Focus on performance improvements in the catalog module (src/catalog/).
```

---

## Git Context

Enable via `.indexer.yaml` to include repository information in the outputs:

```yaml
git:
  include_logs: true
  logs_count: 20
  include_diffs: true
  sort_by_changes: true
  sort_max_commits: 200
```

This adds to the output:
- `recent_commits`: list of commits with hash, author, date, and message
- `diff_stat`: stat of uncommitted changes (staged + unstaged)
- `change_frequency`: map of file → number of commits that touched it

Useful for giving the LLM context about "what changed recently" and "which files are most volatile".

---

## MCP Server

The `--mcp` mode exposes a [Model Context Protocol](https://modelcontextprotocol.io/) JSON-RPC 2.0 server over stdio, for integration with IDEs (Cursor, VS Code + Copilot) and AI agents.

```bash
ai-indexer --mcp ~/projects/my-app
```

### Available tools

| Tool | Parameters | Description |
|---|---|---|
| `get_file_summary` | `file_path: str` | Returns full metadata for a single file |
| `get_dependents` | `file_path: str` | Lists files that import the given file |
| `search_symbol` | `symbol_name: str` | Finds files that define or export a symbol |
| `list_hotspots` | `n: int = 10` | Top N files by priority score |
| `list_orphans` | — | Files with no importers that are not entrypoints |
| `list_by_blast_radius` | `n: int = 10` | Top N files by blast radius |
| `list_refactor_candidates` | `n: int = 10` | Top N files by refactor effort |

### Protocol

Each request is a JSON line on stdin:
```json
{"jsonrpc":"2.0","id":1,"method":"list_hotspots","params":{"n":5}}
```

Each response is a JSON line on stdout:
```json
{"jsonrpc":"2.0","id":1,"result":[{"file":"src/core/engine.py","priority_score":71,...}]}
```

The server runs until stdin is closed (Ctrl-D / EOF).

---

## Audio Tour

Generates a narrated tour of the codebase using the operating system's TTS engine (completely offline):

```bash
# Install dependencies
pip install pyttsx3 pydub

# Generate audio tour
ai-indexer --audio ~/projects/my-app

# With custom speed and background music
ai-indexer --audio --audio-rate 140 --bg-music ~/music/ambient.mp3 ~/projects/my-app
```

The tour narrates: project overview, detected domains, critical files, hotspots, architectural warnings.

Output: `tour_<project-name>.mp3` in the output directory.

> For MP3 background music, `ffmpeg` must be installed on the system (`brew install ffmpeg` on macOS, `apt install ffmpeg` on Ubuntu).

---

## Incremental Cache

The indexer maintains a cache in `.aicontext_cache_v8.json` at the project root. The key is `path:mtime:size` — unmodified files are returned instantly from cache, making repeated runs significantly faster on large codebases.

```bash
# Ignore cache (force full re-analysis)
ai-indexer --no-cache
```

Add to `.gitignore`:
```
.aicontext_cache_v8.json
```

---

## Architecture

```
src/ai_indexer/
├── main.py                  # CLI entrypoint, argument parser, orchestration
├── core/
│   ├── engine.py            # Main engine: file discovery, parallel analysis,
│   │                        # dependency graph, PageRank, metric enrichment
│   ├── models.py            # FileMetadata (__slots__ dataclass), ConfidenceValue
│   └── cache.py             # Incremental per-file cache (key: path:mtime:size)
├── parsers/
│   ├── base.py              # ParseResult + BaseParser ABC + ParserRegistry
│   ├── python.py            # Python parser (tree-sitter or regex fallback)
│   └── typescript.py        # TS/JS/TSX/JSX parser (tree-sitter or regex fallback)
├── exporters/
│   ├── base.py              # BaseExporter ABC
│   ├── toon.py              # TOON exporter (compact columnar format)
│   ├── html.py              # HTML exporter (Nebula dashboard with Three.js)
│   └── xml_exporter.py      # XML exporter (recommended for Claude)
├── mcp/
│   └── server.py            # MCP JSON-RPC 2.0 server over stdio
├── utils/
│   ├── config.py            # .indexer.yaml loader → IndexerConfig
│   ├── io.py                # safe_read_text, count_tokens, ImportResolver,
│   │                        # GitignoreFilter, build_import_resolution_state
│   ├── security.py          # Secret and credential scanner
│   └── git_context.py       # Git context collection (logs, diffs, frequency)
├── audio_tours/
│   ├── narrator.py          # LocalNarrator: TTS synthesis via pyttsx3
│   ├── script_builder.py    # ScriptBuilder: script with phonetic cleanup for TTS
│   └── mixer.py             # Narration + background music mixing (pydub/ffmpeg)
└── tours/
    └── generator.py         # TourGenerator: builds ProjectTour from engine output
```

### Execution flow

```
main.py
  └─ AnalysisEngine.run()
       ├─ _resolve_scan_roots()     # prefer src/ or use root
       ├─ _collect_files()          # filters + include_patterns
       ├─ _analyse_parallel()       # ThreadPoolExecutor
       │    └─ _analyse_file()      # parser + domain + criticality + security scan
       ├─ _build_graph()            # forward + reverse dependency graph
       ├─ _compute_pagerank()       # PageRank iteration
       └─ _enrich_metadata()        # priority_score, refactor_effort, blast_radius
  └─ _build_output()               # builds output dict + instruction + git context
  └─ _write_outputs()              # dispatches to each exporter
```

---

## Language Support

| Language | Extensions | Parser |
|---|---|---|
| Python | `.py` | tree-sitter (fallback: regex) |
| TypeScript | `.ts`, `.tsx` | tree-sitter (fallback: regex) |
| JavaScript | `.js`, `.jsx`, `.mjs`, `.cjs` | tree-sitter (fallback: regex) |
| Others | `.go`, `.rs`, `.java`, `.rb`, `.php`, `.cs`, `.cpp`, `.c`, `.h`, `.swift`, `.kt`, `.json`, `.yaml`, `.toml`, `.md`, and more | Basic text analysis |

---

## Requirements

- **Python 3.11+** (tested on 3.11, 3.12, 3.14)
- Required dependencies: `pydantic>=2.0`, `pathspec>=0.11`
- Optional dependencies: see table in the [Installation](#installation) section

---

## Versioning

This project follows [SemVer](https://semver.org/):

- `PATCH` — bug fixes, minor tweaks (`0.0.5` → `0.0.6`)
- `MINOR` — new features, new exporters, new CLI flags (`0.0.5` → `0.1.0`)
- `MAJOR` — breaking changes to output format or public API

```bash
ai-indexer --version
```

---

## Contributing

```bash
# Clone and install in development mode
git clone https://github.com/LucasSaud/ai-indexer
cd ai-indexer
pip install -e ".[full,dev]"

# Run tests
pytest

# Lint
ruff check src/

# Type checking
mypy src/
```

---

## License

MIT © Lucas Marinho Saud
