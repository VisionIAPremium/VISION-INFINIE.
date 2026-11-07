import tempfile
import unittest
from pathlib import Path

from core.governance.system_audit import run_audit


class SystemAuditTests(unittest.TestCase):
    def test_audit_is_read_only_and_returns_structured_report(self):
        report = run_audit(Path(__file__).resolve().parents[1])
        self.assertEqual(report["audit_mode"], "READ_ONLY")
        self.assertIn(report["overall_status"], {"READY", "READY_WITH_WARNINGS", "FAIL"})
        self.assertGreaterEqual(len(report["checks"]), 7)

    def test_missing_project_files_are_reported(self):
        with tempfile.TemporaryDirectory() as folder:
            report = run_audit(folder)
        structure = next(item for item in report["checks"] if item["name"] == "project_structure")
        self.assertEqual(structure["status"], "FAIL")

    def test_invalid_knowledge_json_is_reported(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "data" / "knowledge"
            path.mkdir(parents=True)
            (path / "knowledge.json").write_text("{invalid", encoding="utf-8")
            report = run_audit(folder)
        knowledge = next(item for item in report["checks"] if item["name"] == "knowledge_store")
        self.assertEqual(knowledge["status"], "FAIL")


if __name__ == "__main__":
    unittest.main()
