import tempfile
import unittest
from pathlib import Path
from core.intelligence.engine import add_entry, list_entries, search_entries

class KnowledgeEngineTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.store = Path(self.temp_dir.name) / "knowledge.json"

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_add_and_list_entry(self):
        created = add_entry("System vision", "Build intelligent systems.", ["vision"], self.store)
        entries = list_entries(self.store)
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]["id"], created["id"])
        self.assertEqual(entries[0]["tags"], ["vision"])

    def test_search_ranks_title_match(self):
        add_entry("Automation", "Workflow execution.", ["ops"], self.store)
        add_entry("Knowledge", "Automation strategy and intelligence.", ["vision"], self.store)
        results = search_entries("automation", store_path=self.store)
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["title"], "Automation")

    def test_rejects_empty_title(self):
        with self.assertRaises(ValueError):
            add_entry(" ", "Some content", store_path=self.store)

    def test_empty_query_returns_no_results(self):
        add_entry("Knowledge", "Useful content.", store_path=self.store)
        self.assertEqual(search_entries("   ", store_path=self.store), [])

if __name__ == "__main__":
    unittest.main()
