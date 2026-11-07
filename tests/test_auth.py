import unittest
from core.governance.auth import AuthenticationError, authenticate_header, issue_token, verify_token
from core.governance.authority import Role

SECRET = b"test-secret-with-at-least-32-bytes-long"

class AuthenticationTests(unittest.TestCase):
    def test_issues_and_verifies_founder_token(self):
        token = issue_token("founder-test", Role.FOUNDER, SECRET, 600)
        claims = verify_token(token, SECRET)
        self.assertEqual(claims.subject, "founder-test")
        self.assertEqual(claims.role, Role.FOUNDER)

    def test_header_requires_bearer_scheme(self):
        token = issue_token("director-test", Role.DIRECTOR, SECRET, 600)
        self.assertEqual(authenticate_header("Bearer " + token, SECRET).role, Role.DIRECTOR)
        with self.assertRaises(AuthenticationError):
            authenticate_header("Basic " + token, SECRET)

    def test_tampered_token_is_rejected(self):
        token = issue_token("founder-test", Role.FOUNDER, SECRET, 600)
        altered = token[:-1] + ("A" if token[-1] != "A" else "B")
        with self.assertRaises(AuthenticationError):
            verify_token(altered, SECRET)

    def test_expired_token_is_rejected(self):
        token = issue_token("founder-test", Role.FOUNDER, SECRET, 60)
        claims = verify_token(token, SECRET)
        with self.assertRaises(AuthenticationError):
            verify_token(token, SECRET, now=claims.expires_at)

    def test_invalid_secret_and_ttl_are_rejected(self):
        with self.assertRaises(ValueError):
            issue_token("founder-test", Role.FOUNDER, b"short", 600)
        with self.assertRaises(ValueError):
            issue_token("founder-test", Role.FOUNDER, SECRET, 10)

if __name__ == "__main__":
    unittest.main()
