#!/usr/bin/env python3
"""Serve the loop status dashboard from the project root.

Static page: docs/dashboard/loop_status.html
JSON / PDF are fetched via relative paths under state/, Results/, Submissions/.

Usage:
  python3 scripts/serve_dashboard.py
  python3 scripts/serve_dashboard.py --port 8765 --no-open
"""

from __future__ import annotations

import argparse
import functools
import sys
import webbrowser
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DASHBOARD = "/docs/dashboard/loop_status.html"
DEFAULT_PORT = 8765


class RootHandler(SimpleHTTPRequestHandler):
    """Serve repo root; map / → dashboard; set MIME for json/jsonl/pdf."""

    extensions_map = {
        **getattr(SimpleHTTPRequestHandler, "extensions_map", {}),
        ".json": "application/json; charset=utf-8",
        ".jsonl": "application/jsonl; charset=utf-8",
        ".md": "text/markdown; charset=utf-8",
        ".pdf": "application/pdf",
        ".html": "text/html; charset=utf-8",
    }

    def __init__(self, *args, directory: str | None = None, **kwargs):
        super().__init__(*args, directory=directory, **kwargs)

    def do_GET(self) -> None:  # noqa: N802
        if self.path in ("/", ""):
            self.send_response(302)
            self.send_header("Location", DASHBOARD)
            self.end_headers()
            return
        return super().do_GET()

    def log_message(self, fmt: str, *args) -> None:
        sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))


def main() -> int:
    parser = argparse.ArgumentParser(description="Serve loop status dashboard")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--no-open", action="store_true", help="Do not open browser")
    args = parser.parse_args()

    page = ROOT / "docs" / "dashboard" / "loop_status.html"
    if not page.is_file():
        print("ERROR: docs/dashboard/loop_status.html missing", file=sys.stderr)
        return 1

    handler = functools.partial(RootHandler, directory=str(ROOT))
    try:
        server = ThreadingHTTPServer((args.host, args.port), handler)
    except OSError as exc:
        print(f"ERROR: cannot bind {args.host}:{args.port} · {exc}", file=sys.stderr)
        return 1

    url = f"http://{args.host}:{args.port}{DASHBOARD}"
    print("Loop status dashboard")
    print(f"  root: {ROOT}")
    print(f"  open: {url}")
    print("  stop: Ctrl+C")
    if not args.no_open:
        try:
            webbrowser.open(url)
        except Exception:
            pass
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped")
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
