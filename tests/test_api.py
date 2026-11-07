"""HTTP API integration tests using an isolated in-process server."""
import json
import os
import threading
import unittest
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from unittest.mock import patch

from app import VisionHandler, VisionHTTPServer
from core.governance.auth import issue_token
from core.governance.authority import Role

SECRET = b"api-test-secret-with-at-least-32-bytes"


class StubCore:
    def ask(self, question):
        return {"answer": question, "provider": "test"}


class ApiIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.env_patch = patch.dict(
            os.environ,
            {"VISION_INFINIE_TOKEN_SECRET": SECRET.decode("ascii")},
        )
        self.env_patch.start()
        self.original_core = VisionHandler.core
        VisionHandler.core = StubCore()
        self.audit_patch = patch("app.record_event")
        self.audit_patch.start()
        self.server = VisionHTTPServer(("127.0.0.1", 0), VisionHandler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.base_url = f"http://127.0.0.1:{self.server.server_port}"

    def tearDown(self):
        self.server.shutdown()
        self.thread.join(timeout=2)
        self.server.server_close()
        self.audit_patch.stop()
        VisionHandler.core = self.original_core
        self.env_patch.stop()

    def request(self, method, path, data=None, token=None, content_length=None):
        headers = {}
        if data is not None:
            headers["Content-Type"] = "application/json"
        if token is not None:
            headers["Authorization"] = "Bearer " + token
        if content_length is not None:
            headers["Content-Length"] = str(content_length)
        request = Request(self.base_url + path, data=data, headers=headers, method=method)
        try:
            with urlopen(request, timeout=3) as response:
                return response.status, response.read()
        except HTTPError as error:
            return error.code, error.read()

    def test_health_is_public(self):
        status, body = self.request("GET", "/health")
        self.assertEqual(status, 200)
        self.assertEqual(json.loads(body)["status"], "ok")

    def test_ask_requires_authentication(self):
        status, _ = self.request("POST", "/ask", data=b'{"question":"hello"}')
        self.assertEqual(status, 401)

    def test_agent_role_cannot_call_ask(self):
        token = issue_token("agent-test", Role.AGENT, SECRET, 600)
        status, _ = self.request("POST", "/ask", data=b'{"question":"hello"}', token=token)
        self.assertEqual(status, 403)

    def test_founder_can_call_ask(self):
        token = issue_token("founder-test", Role.FOUNDER, SECRET, 600)
        status, body = self.request("POST", "/ask", data=b'{"question":"hello"}', token=token)
        self.assertEqual(status, 200)
        self.assertEqual(json.loads(body)["answer"], "hello")

    def test_invalid_json_is_rejected(self):
        token = issue_token("founder-test", Role.FOUNDER, SECRET, 600)
        status, _ = self.request("POST", "/ask", data=b"{invalid", token=token)
        self.assertEqual(status, 400)

    def test_oversized_body_is_rejected(self):
        token = issue_token("founder-test", Role.FOUNDER, SECRET, 600)
        status, _ = self.request(
            "POST", "/ask", data=b"x" * 16385, token=token, content_length=16385
        )
        self.assertEqual(status, 413)


if __name__ == "__main__":
    unittest.main()
