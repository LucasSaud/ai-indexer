"""Minimal stdlib HTTP server that exposes MCP query methods as REST endpoints.

Start with ``ai-indexer --serve [PORT]`` (default 8765).

Endpoints
---------
GET /hotspots?n=10
GET /file?path=src/foo.py
GET /subgraph?path=src/foo.py&depth=2
GET /search?symbol=MyClass
GET /blast_radius?n=10
GET /refactor_candidates?n=10
GET /orphans
"""

from __future__ import annotations

import json
import logging
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import TYPE_CHECKING, Any
from urllib.parse import parse_qs, urlparse

if TYPE_CHECKING:
    from ai_indexer.core.models import FileMetadata

log = logging.getLogger("ai-indexer.http")


class _Handler(BaseHTTPRequestHandler):
    """Request handler — set `_server` class attribute before use."""

    _mcp: Any = None  # MCPServer instance, set by HttpMcpServer.serve()

    def log_message(self, fmt: str, *args: Any) -> None:  # noqa: D401
        log.debug(fmt, *args)

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        qs     = parse_qs(parsed.query)

        def first(key: str, default: str = "") -> str:
            return qs.get(key, [default])[0]

        path = parsed.path.rstrip("/")
        try:
            if path == "/hotspots":
                result = self._mcp.list_hotspots(int(first("n", "10")))
            elif path == "/file":
                result = self._mcp.get_file_summary(first("path"))
            elif path == "/subgraph":
                result = self._mcp.get_subgraph(first("path"), int(first("depth", "2")))
            elif path == "/search":
                result = self._mcp.search_symbol(first("symbol"))
            elif path == "/blast_radius":
                result = self._mcp.list_by_blast_radius(int(first("n", "10")))
            elif path == "/refactor_candidates":
                result = self._mcp.list_refactor_candidates(int(first("n", "10")))
            elif path == "/orphans":
                result = self._mcp.list_orphans()
            elif path == "/dependents":
                result = self._mcp.get_dependents(first("path"))
            else:
                self._send(404, {"error": f"Unknown endpoint: {path}"})
                return
        except Exception as exc:  # noqa: BLE001
            self._send(500, {"error": str(exc)})
            return

        self._send(200, result)

    def _send(self, status: int, body: Any) -> None:
        payload = json.dumps(body, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(payload)


class HttpMcpServer:
    """Wrap an MCPServer instance in a plain stdlib HTTP server."""

    def __init__(
        self,
        files: dict[str, "FileMetadata"],
        graph: dict[str, list[str]],
        reverse_graph: dict[str, list[str]],
        port: int = 8765,
    ) -> None:
        from ai_indexer.mcp.server import MCPServer
        self._mcp  = MCPServer(files, graph, reverse_graph)
        self._port = port

    def serve(self) -> None:
        # Inject the MCP instance into the handler class before starting
        _Handler._mcp = self._mcp
        server = HTTPServer(("", self._port), _Handler)
        log.info("HTTP MCP server listening on http://localhost:%d", self._port)
        print(f"  Serving on http://localhost:{self._port}  (Ctrl-C to stop)", flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
        finally:
            server.server_close()
