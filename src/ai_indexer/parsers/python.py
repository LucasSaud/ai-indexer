"""Python language parser (AST-primary, regex fallback)."""

from __future__ import annotations

import ast
import re
from pathlib import Path
from typing import TYPE_CHECKING

from ai_indexer.parsers.base import BaseParser, ParseResult

if TYPE_CHECKING:
    from ai_indexer.utils.io import ImportResolver

_PY_STDLIB_PREFIXES = frozenset({
    "os", "sys", "re", "io", "abc", "ast", "copy", "csv", "datetime",
    "enum", "functools", "hashlib", "http", "json", "logging", "math",
    "pathlib", "random", "shutil", "subprocess", "time", "typing",
    "unittest", "urllib", "uuid", "collections", "contextlib", "dataclasses",
    "asyncio", "itertools", "threading", "multiprocessing", "tempfile",
    "socket", "statistics", "decimal", "fractions", "inspect", "importlib",
    "pkgutil", "traceback", "warnings", "sqlite3", "ssl", "email",
    "selectors", "queue", "tomllib", "struct", "array", "bisect",
    "heapq", "weakref", "types", "typing_extensions",
})

_RE_PY_FUNC  = re.compile(r"^\s*(?:async\s+)?def\s+([A-Za-z_]\w*)\s*\(", re.MULTILINE)
_RE_PY_CLASS = re.compile(r"^\s*class\s+([A-Za-z_]\w*)\b", re.MULTILINE)
_RE_PY_MAIN  = re.compile(r"if\s+__name__\s*==\s*['\"]__main__['\"]")


class PythonParser(BaseParser):
    extensions = frozenset({".py"})

    def parse(self, path: Path, src: str, resolver: "ImportResolver") -> ParseResult:
        result = ParseResult()
        try:
            tree = ast.parse(src, filename=str(path))
        except SyntaxError:
            tree = None

        if tree is not None:
            self._walk_ast(tree, path, src, resolver, result)
        else:
            # Regex fallback when AST fails (e.g., partial file, encoding issues)
            result.functions.extend(m.group(1) for m in _RE_PY_FUNC.finditer(src))
            result.classes.extend(m.group(1) for m in _RE_PY_CLASS.finditer(src))

        result.has_main_guard = bool(_RE_PY_MAIN.search(src))
        return result

    def _walk_ast(
        self,
        tree: ast.Module,
        path: Path,
        src: str,
        resolver: "ImportResolver",
        result: ParseResult,
    ) -> None:
        module_doc = ast.get_docstring(tree)
        if module_doc:
            result.module_doc = module_doc.strip()

        external: set[str] = set()
        internal: set[str] = set()

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    mod = alias.name
                    base = mod.split(".")[0]
                    resolved = resolver.resolve_import(mod, path, "py")
                    if resolved:
                        internal.add(resolved)
                    elif base not in _PY_STDLIB_PREFIXES:
                        external.add(base)

            elif isinstance(node, ast.ImportFrom):
                mod = node.module or ""
                spec = "." * node.level + mod if node.level else mod
                resolved = resolver.resolve_import(spec or mod, path, "py")
                if resolved:
                    internal.add(resolved)
                else:
                    base = mod.split(".")[0] if mod else ""
                    if base and base not in _PY_STDLIB_PREFIXES:
                        external.add(base)

            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                result.functions.append(node.name)
                doc = ast.get_docstring(node)
                if doc:
                    result.docstrings[node.name] = doc.strip().split("\n")[0]
                hints: dict[str, str] = {}
                for arg in node.args.args:
                    if arg.annotation:
                        hints[arg.arg] = ast.unparse(arg.annotation)
                if node.returns:
                    hints["return"] = ast.unparse(node.returns)
                if hints:
                    result.type_hints[node.name] = hints

            elif isinstance(node, ast.ClassDef):
                result.classes.append(node.name)
                doc = ast.get_docstring(node)
                if doc:
                    result.docstrings[node.name] = doc.strip().split("\n")[0]

        result.external = sorted(external)
        result.internal = sorted(internal)
        result.functions = list(dict.fromkeys(result.functions))[:20]
        result.classes   = list(dict.fromkeys(result.classes))[:20]

        # Second pass: collect intra-file call targets per top-level function / method
        for top in ast.iter_child_nodes(tree):
            if isinstance(top, (ast.FunctionDef, ast.AsyncFunctionDef)):
                result.calls[top.name] = self._collect_calls(top)
            elif isinstance(top, ast.ClassDef):
                for item in ast.iter_child_nodes(top):
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        result.calls[item.name] = self._collect_calls(item)

    @staticmethod
    def _collect_calls(
        fn: "ast.FunctionDef | ast.AsyncFunctionDef",
    ) -> list[str]:
        """Return deduplicated call targets (max 8) within *fn*'s body."""
        seen: list[str] = []
        for child in ast.walk(fn):
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Name):
                    seen.append(child.func.id)
                elif isinstance(child.func, ast.Attribute):
                    base = child.func.value
                    if isinstance(base, ast.Name) and base.id != "self":
                        seen.append(f"{base.id}.{child.func.attr}")
                    else:
                        seen.append(child.func.attr)
        return list(dict.fromkeys(seen))[:8]

    def chunk(self, src: str, path: Path, max_tokens: int = 800) -> list[str]:
        from ai_indexer.utils.io import count_tokens
        try:
            tree = ast.parse(src)
            chunks: list[str] = []
            current: list[str] = []
            current_tokens = 0
            for node in ast.iter_child_nodes(tree):
                node_str = ast.unparse(node)
                node_tokens = count_tokens(node_str)
                if current_tokens + node_tokens > max_tokens and current:
                    chunks.append("\n".join(current))
                    current = [node_str]
                    current_tokens = node_tokens
                else:
                    current.append(node_str)
                    current_tokens += node_tokens
            if current:
                chunks.append("\n".join(current))
            return chunks
        except Exception:
            return super().chunk(src, path, max_tokens)
