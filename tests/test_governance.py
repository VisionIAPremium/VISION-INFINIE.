import json
import tempfile
import unittest
from pathlib import Path

from core.governance.audit import record_event


class GovernanceTests(unittest.TestCase):
    def test_audit_event_is_written_as_jsonl(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "events.jsonl"
            event = record_event("test.event", "test detail", path)
            stored = json.loads(path.read_text(encoding="utf-8").strip())
            self.assertEqual(stored["event_type"], event["event_type"])
            self.assertEqual(stored["detail"], "test detail")

    def test_audit_rejects_empty_fields(self):
        with self.assertRaises(ValueError):
            record_event("", "detail")


if __name__ == "__main__":
    unittest.main()
