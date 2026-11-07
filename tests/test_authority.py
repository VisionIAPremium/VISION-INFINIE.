import unittest

from core.governance.authority import (
    Decision,
    Role,
    authorize_action,
    can_route_message,
)


class AuthorityTests(unittest.TestCase):
    def test_founder_and_director_are_the_only_user_facing_chain(self):
        self.assertTrue(can_route_message(Role.FOUNDER, Role.DIRECTOR))
        self.assertTrue(can_route_message(Role.DIRECTOR, Role.FOUNDER))
        self.assertFalse(can_route_message(Role.AGENT, Role.FOUNDER))

    def test_agents_report_to_director_only(self):
        self.assertTrue(can_route_message(Role.AGENT, Role.DIRECTOR))
        self.assertTrue(can_route_message(Role.DIRECTOR, Role.AGENT))
        self.assertFalse(can_route_message(Role.AGENT, Role.FOUNDER))

    def test_agent_action_denied_until_director_approval(self):
        result = authorize_action(Role.AGENT, "prepare_draft")
        self.assertEqual(result.decision, Decision.DENY)
        self.assertEqual(result.approver, Role.DIRECTOR)

    def test_agent_reserved_action_is_escalated_after_director_review(self):
        result = authorize_action(
            Role.AGENT, "connect_external_service", director_approved=True
        )
        self.assertEqual(result.decision, Decision.REQUIRE_FOUNDER)
        approved = authorize_action(
            Role.AGENT, "connect_external_service",
            director_approved=True, founder_approved=True
        )
        self.assertEqual(approved.decision, Decision.ALLOW)

    def test_director_can_approve_delegated_actions(self):
        result = authorize_action(Role.DIRECTOR, "run_local_tests")
        self.assertEqual(result.decision, Decision.ALLOW)

    def test_reserved_action_requires_founder_approval(self):
        pending = authorize_action(Role.DIRECTOR, "connect_external_service")
        self.assertEqual(pending.decision, Decision.REQUIRE_FOUNDER)
        approved = authorize_action(
            Role.DIRECTOR, "connect_external_service", founder_approved=True
        )
        self.assertEqual(approved.decision, Decision.ALLOW)

    def test_empty_action_is_rejected(self):
        with self.assertRaises(ValueError):
            authorize_action(Role.DIRECTOR, "")


if __name__ == "__main__":
    unittest.main()
