import tempfile
import unittest
from pathlib import Path

from core.ai.orchestrator import AICore
from core.ai.provider import LocalContextProvider
from core.memory.store import MemoryStore


class AICoreTests(unittest.TestCase):
    def test_local_provider_reports_missing_context(self):
        result = LocalContextProvider().generate("unknown question", [])
        self.assertIn("aucun élément", result)

    def test_memory_persists_and_searches(self):
        with tempfile.TemporaryDirectory() as directory:
            memory = MemoryStore(Path(directory) / "memory.sqlite3")
            memory.add("VISION INFINIE architecture intelligente")
            hits = memory.search("architecture")
            self.assertEqual(len(hits), 1)
            self.assertIn("VISION INFINIE", hits[0]["content"])

    def test_orchestrator_uses_local_provider(self):
        with tempfile.TemporaryDirectory() as directory:
            memory = MemoryStore(Path(directory) / "memory.sqlite3")
            memory.add("Le projet utilise une architecture modulaire.")
            core = AICore(memory=memory)
            result = core.ask("architecture")
            self.assertEqual(result["provider"], "LocalContextProvider")
            self.assertEqual(result["memory_hits"], 1)
            self.assertIn("architecture modulaire", result["answer"])

    def test_empty_question_is_rejected(self):
        with self.assertRaises(ValueError):
            AICore().ask("  ")


if __name__ == "__main__":
    unittest.main()
