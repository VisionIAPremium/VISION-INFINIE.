import tempfile
import unittest
from pathlib import Path

from core.ai.orchestrator import AICore
from core.ai.provider import LocalContextProvider
from core.agents.registry import AgentSpec, register_agent
from core.director.director import AgentReport, Director
from core.memory.store import MemoryStore


class DirectorTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        memory = MemoryStore(Path(self.temp.name) / "memory.sqlite3")
        memory.add("VISION INFINIE utilise une architecture modulaire.")
        self.director = Director(AICore(provider=LocalContextProvider(), memory=memory))

    def tearDown(self):
        self.temp.cleanup()

    def test_founder_instruction_is_answered_through_director(self):
        result = self.director.receive_founder_instruction("architecture")
        self.assertEqual(result["channel"], "director_to_founder")
        self.assertIn("architecture modulaire", result["answer"])

    def test_director_assigns_task_to_registered_agent(self):
        register_agent(AgentSpec("research-test", "Research test agent"))
        task = self.director.assign_agent_task("research-test", "Prepare a summary")
        self.assertEqual(task.status, "assigned")

    def test_agent_report_must_match_director_task(self):
        register_agent(AgentSpec("report-test", "Report test agent"))
        task = self.director.assign_agent_task("report-test", "Prepare a summary")
        with self.assertRaises(ValueError):
            self.director.receive_agent_report(AgentReport("wrong-id", "report-test", "Done"))
        self.director.receive_agent_report(AgentReport(task.task_id, "report-test", "Summary ready"))
        briefing = self.director.prepare_founder_briefing(task.task_id)
        self.assertEqual(briefing["channel"], "director_to_founder")
        self.assertEqual(briefing["report"], "Summary ready")

    def test_director_cannot_brief_founder_without_agent_report(self):
        register_agent(AgentSpec("pending-test", "Pending test agent"))
        task = self.director.assign_agent_task("pending-test", "Prepare a summary")
        with self.assertRaises(ValueError):
            self.director.prepare_founder_briefing(task.task_id)

    def test_empty_founder_instruction_is_rejected(self):
        with self.assertRaises(ValueError):
            self.director.receive_founder_instruction(" ")


if __name__ == "__main__":
    unittest.main()