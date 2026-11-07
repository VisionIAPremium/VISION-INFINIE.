"""Local-only HTTP API for the VISION INFINIE AI Core.

By default this server binds to 127.0.0.1 and is not intended for public hosting.
"""
from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, HTTPServer

from core.ai.orchestrator import AICore
from core.memory.store import MemoryStore
from core.governance.audit import record_event


class VisionHandler(BaseHTTPRequestHandler):
    core = AICore(memory=MemoryStore())

    def _send(self, status: int, payload: dict) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/health":
            self._send(200, {"status": "ok", "service": "VISION INFINIE AI Core"})
        else:
            self._send(404, {"error": "Not found"})

    def do_POST(self):
        if self.path != "/ask":
            self._send(404, {"error": "Not found"})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length < 1 or length > 16_384:
                self._send(413, {"error": "Request body must be between 1 and 16384 bytes"})
                return
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
            question = payload.get("question", "")
            result = self.core.ask(question)
            record_event("ai_core.ask", "Local question processed")
            self._send(200, result)
        except (UnicodeDecodeError, json.JSONDecodeError, AttributeError, ValueError) as exc:
            self._send(400, {"error": str(exc)})

    def log_message(self, format, *args):
        return


def main():
    server = HTTPServer(("127.0.0.1", 8765), VisionHandler)
    print("VISION INFINIE API available at http://127.0.0.1:8765")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
