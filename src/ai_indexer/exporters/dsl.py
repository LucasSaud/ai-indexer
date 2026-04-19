"""DSL (Domain-Specific Language) exporter.

Produces a compact, function-aware textual representation optimised for LLM
consumption. Prioritises density over completeness: each file costs roughly
2–6 lines instead of 40+ lines of JSON.

Format
------
# ai-indexer DSL v0.0.7 | project | 30 files | 3 domains | 2026-04-17
# Hotspots: src/ai_indexer/main.py  src/ai_indexer/core/engine.py

[MOD:core/critical] src/ai_indexer/core/engine.py
  [DOC] Analysis engine — orchestrates parsing, graph building, metric enrichment
  [CLS] AnalysisEngine
  [FN] run -> _collect_files _analyse_parallel _build_graph _enrich
  [FN] _analyse_file -> scan_secrets safe_read_text count_tokens
  [DEP] src/ai_indexer/core/cache.py  src/ai_indexer/core/models.py

[MOD:utils/supporting] src/ai_indexer/parsers/python.py
  [FN] parse  chunk

Notations
---------
[MOD:layer/criticality]  — file header (layer = first char of layer field)
[DOC]  — first 80 chars of role_hint (first line only)
[CLS]  — space-separated class names (max 6)
[FN] name -> call1 call2  — function with known callees (max 4 targets shown)
[FN] name1 name2 ...  — grouped no-callees line (max 8 per line)
[DEP]  — internal dependency paths (max 4)
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any

from ai_indexer.exporters.base import BaseExporter

if TYPE_CHECKING:
    pass

# File types that carry no meaningful code — skip entirely in DSL
_SKIP_TYPES = frozenset({"config", "asset", "template", "docs"})


class DslExporter(BaseExporter):
    extension = ".dsl"

    def export(self, data: dict[str, Any], output_path: Path) -> None:
        output_path.write_text(self._render(data), encoding="utf-8")

    # ── Public: single-file block (used by MCP get_dsl_chunk) ────────────────

    def render_file(self, path: str, fd: Any) -> str:
        """Return the DSL block string for one FileMetadata object."""
        if hasattr(fd, "to_dict"):
            d = fd.to_dict(compact=True)
            d["_fc"] = fd.func_calls
            d["_deps"] = fd.internal_dependencies
            d["_type"] = fd.file_type.value
        else:
            d = dict(fd)
            d["_fc"]   = d.get("fc") or d.get("func_calls", {})
            d["_deps"] = d.get("ideps") or d.get("internal_dependencies", [])
            d["_type"] = (d.get("ft") or {}).get("value", "")
        return self._render_block(path, d)

    # ── Rendering ─────────────────────────────────────────────────────────────

    def _render(self, data: dict[str, Any]) -> str:
        files    = data.get("files") or {}
        stats    = data.get("stats") or {}
        hotspots = data.get("hotspots") or []
        version  = data.get("version", "")
        project  = data.get("project", "")
        ts       = datetime.now().strftime("%Y-%m-%d")

        n_files   = stats.get("total_files", len(files))
        n_domains = stats.get("domains", 0)

        top3 = "  ".join(h["file"] for h in hotspots[:3])

        lines = [
            f"# ai-indexer DSL {version} | {project} | {n_files} files | {n_domains} domains | {ts}",
            f"# Hotspots: {top3}",
            "",
        ]

        # Sort by priority_score descending
        sorted_items = sorted(
            files.items(),
            key=lambda kv: kv[1].get("ps") or kv[1].get("priority_score", 0),
            reverse=True,
        )

        for path, fd in sorted_items:
            ftype = (fd.get("ft") or {}).get("value") or fd.get("file_type", "")
            if ftype in _SKIP_TYPES:
                continue
            block = self._render_block(path, self._norm(fd))
            if block:
                lines.append(block)
                lines.append("")

        return "\n".join(lines)

    def _norm(self, fd: dict[str, Any]) -> dict[str, Any]:
        """Normalise a compact-dict fd into a consistent internal representation."""
        out = dict(fd)
        out["_fc"]   = fd.get("fc") or fd.get("func_calls", {})
        out["_deps"] = fd.get("ideps") or fd.get("internal_dependencies", [])
        out["_type"] = (fd.get("ft") or {}).get("value") or fd.get("file_type", "")
        return out

    def _render_block(self, path: str, fd: dict[str, Any]) -> str:
        layer     = (fd.get("l") or fd.get("layer") or "u")
        layer_ch  = layer[0] if layer else "u"
        crit      = (fd.get("c") or fd.get("criticality") or "s")
        # Expand single-char criticality
        _crit_map = {"c": "critical", "i": "infra", "s": "supporting", "u": "unknown"}
        crit_full = _crit_map.get(crit, crit) if len(crit) == 1 else crit

        lines = [f"[MOD:{layer_ch}/{crit_full}] {path}"]

        # [DOC]
        rh = (fd.get("rh") or fd.get("role_hint") or "").strip()
        if rh:
            first_line = rh.splitlines()[0][:80]
            lines.append(f"  [DOC] {first_line}")

        # [CLS]
        caps  = fd.get("caps") or fd.get("capabilities") or {}
        classes = caps.get("classes", [])[:6]
        if classes:
            lines.append(f"  [CLS] {' '.join(classes)}")

        # [FN] — functions with call targets, then grouped no-call functions
        fc       = fd.get("_fc") or {}
        funcs    = caps.get("functions", [])
        if funcs:
            no_call: list[str] = []
            for fn in funcs[:12]:
                targets = fc.get(fn, [])[:4]
                if targets:
                    lines.append(f"  [FN] {fn} -> {' '.join(targets)}")
                else:
                    no_call.append(fn)
            # Group remaining no-call functions, max 8 per line
            for i in range(0, len(no_call[:8]), 8):
                chunk = no_call[i:i+8]
                lines.append(f"  [FN] {' '.join(chunk)}")

        # [DEP]
        deps = (fd.get("_deps") or [])[:4]
        if deps:
            lines.append(f"  [DEP] {'  '.join(deps)}")

        # If only the header line was produced and there's nothing interesting, skip
        if len(lines) == 1:
            ps = fd.get("ps") or fd.get("priority_score", 0)
            if ps < 35:
                return ""   # skip low-priority files with no capabilities

        return "\n".join(lines)
