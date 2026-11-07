import unittest
from core.decision.engine import evaluate
from core.agents.registry import AgentSpec, register_agent, list_agents, get_agent
from core.automation.approval import propose_action, authorize_action

class SystemFoundationTests(unittest.TestCase):
    def test_decision_requires_review_when_checks_missing(self):
        self.assertEqual(evaluate({}).outcome, "needs_review")

    def test_decision_explains_failed_check(self):
        result = evaluate({"identity_verified": True, "consent": False})
        self.assertEqual(result.outcome, "needs_review")
        self.assertIn("Check failed: consent", result.reasons)

    def test_decision_eligible_when_all_checks_pass(self):
        self.assertEqual(evaluate({"consent": True}).outcome, "eligible")

    def test_agent_registry_defaults_to_human_approval(self):
        spec = AgentSpec("knowledge-curator", "Organizes approved knowledge.")
        register_agent(spec)
        self.assertTrue(get_agent("knowledge-curator").requires_human_approval)
        self.assertEqual(len(list_agents()), 1)

    def test_automation_never_executes(self):
        proposal = propose_action("Prepare a draft report")
        approved = authorize_action(proposal, True)
        self.assertEqual(approved.status, "approved_for_manual_execution")

    def test_rejected_proposal(self):
        proposal = propose_action("Send an email")
        rejected = authorize_action(proposal, False)
        self.assertEqual(rejected.status, "rejected")

if __name__ == "__main__":
    unittest.main()
