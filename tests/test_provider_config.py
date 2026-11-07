import json
import os
import unittest
from unittest.mock import patch
from core.ai.config import build_provider
from core.ai.provider import LocalContextProvider, OpenAICompatibleProvider

class ProviderConfigurationTests(unittest.TestCase):
    def test_defaults_to_local_provider(self):
        with patch.dict(os.environ, {}, clear=True):
            self.assertIsInstance(build_provider(), LocalContextProvider)

    def test_builds_openai_compatible_provider(self):
        env = {"VISION_INFINIE_PROVIDER": "openai-compatible", "VISION_INFINIE_BASE_URL": "https://example.test/v1", "VISION_INFINIE_MODEL": "test-model"}
        with patch.dict(os.environ, env, clear=True):
            provider = build_provider()
        self.assertIsInstance(provider, OpenAICompatibleProvider)
        self.assertEqual(provider.base_url, "https://example.test/v1")
        self.assertEqual(provider.model, "test-model")

    def test_remote_provider_requires_endpoint_and_model(self):
        with patch.dict(os.environ, {"VISION_INFINIE_PROVIDER": "openai-compatible"}, clear=True):
            with self.assertRaises(ValueError):
                build_provider()

    def test_unknown_provider_is_rejected(self):
        with patch.dict(os.environ, {"VISION_INFINIE_PROVIDER": "unknown"}, clear=True):
            with self.assertRaises(ValueError):
                build_provider()

    def test_remote_request_and_response_are_parsed(self):
        class FakeResponse:
            def __enter__(self): return self
            def __exit__(self, *args): return False
            def read(self):
                return json.dumps({"choices": [{"message": {"content": "Réponse de test"}}]}).encode("utf-8")
        provider = OpenAICompatibleProvider(base_url="https://example.test/v1", model="test-model")
        with patch.dict(os.environ, {"VISION_INFINIE_API_KEY": "test-key"}):
            with patch("core.ai.provider.urlopen", return_value=FakeResponse()) as mocked:
                answer = provider.generate("Question ?", [], "Instruction")
        self.assertEqual(answer, "Réponse de test")
        request = mocked.call_args.args[0]
        self.assertEqual(request.full_url, "https://example.test/v1/chat/completions")
        self.assertEqual(request.get_header("Authorization"), "Bearer test-key")

    def test_missing_api_key_fails_before_network_call(self):
        provider = OpenAICompatibleProvider(base_url="https://example.test/v1", model="test-model")
        with patch.dict(os.environ, {}, clear=True):
            with patch("core.ai.provider.urlopen") as mocked:
                with self.assertRaisesRegex(RuntimeError, "Missing API key"):
                    provider.generate("Question ?", [])
                mocked.assert_not_called()

    def test_unexpected_response_shape_is_rejected(self):
        class FakeResponse:
            def __enter__(self): return self
            def __exit__(self, *args): return False
            def read(self): return b'{"unexpected": true}'
        provider = OpenAICompatibleProvider(base_url="https://example.test/v1", model="test-model")
        with patch.dict(os.environ, {"VISION_INFINIE_API_KEY": "test-key"}):
            with patch("core.ai.provider.urlopen", return_value=FakeResponse()):
                with self.assertRaisesRegex(RuntimeError, "unexpected response format"):
                    provider.generate("Question ?", [])

if __name__ == "__main__":
    unittest.main()
