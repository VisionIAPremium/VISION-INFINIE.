"""Authenticated HTTP API. Use a TLS reverse proxy for internet deployment."""
from __future__ import annotations
import json, os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from core.ai.orchestrator import AICore
from core.governance.audit import record_event
from core.governance.auth import AuthenticationError, authenticate_header, get_token_secret
from core.governance.authority import Role
from core.memory.store import MemoryStore

class VisionHTTPServer(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True

class VisionHandler(BaseHTTPRequestHandler):
    core = AICore(memory=MemoryStore())

    def _send(self, status: int, payload: dict) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Referrer-Policy", "no-referrer")
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
            claims = authenticate_header(self.headers.get("Authorization"), get_token_secret())
        except (AuthenticationError, RuntimeError):
            self._send(401, {"error": "Unauthorized"})
            return
        if claims.role not in (Role.FOUNDER, Role.DIRECTOR):
            self._send(403, {"error": "Forbidden"})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length < 1 or length > 16384:
                self._send(413, {"error": "Request body must be between 1 and 16384 bytes"})
                return
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
            if not isinstance(payload, dict):
                raise ValueError("JSON body must be an object.")
            question = payload.get("question", "")
            if not isinstance(question, str) or not question.strip():
                raise ValueError("Question must be a non-empty string.")
            result = self.core.ask(question)
            record_event("ai_core.ask", f"Authenticated request by {claims.subject} ({claims.role.value}).")
            self._send(200, result)
        except (UnicodeDecodeError, json.JSONDecodeError, AttributeError, ValueError):
            self._send(400, {"error": "Invalid request."})

    def log_message(self, format, *args):
        return

def main():
    host = os.getenv("VISION_INFINIE_HOST", "127.0.0.1")
    port = int(os.getenv("VISION_INFINIE_PORT", "8765"))
    if host not in ("127.0.0.1", "localhost", "0.0.0.0"):
        raise RuntimeError("VISION_INFINIE_HOST must be localhost or 0.0.0.0.")
    server = VisionHTTPServer((host, port), VisionHandler)
    print(f"VISION INFINIE API listening on {host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()

if __name__ == "__main__":
    main()
