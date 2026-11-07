"""Provider selection from explicit environment configuration."""
from __future__ import annotations
import os
from core.ai.provider import LocalContextProvider, OpenAICompatibleProvider, ModelProvider

def build_provider() -> ModelProvider:
    """Build the configured provider; default safely to the offline provider."""
    selected = os.getenv("VISION_INFINIE_PROVIDER", "local").strip().lower()
    if selected == "local":
        return LocalContextProvider()
    if selected == "openai-compatible":
        base_url = os.getenv("VISION_INFINIE_BASE_URL", "").strip()
        model = os.getenv("VISION_INFINIE_MODEL", "").strip()
        if not base_url or not model:
            raise ValueError("OpenAI-compatible provider requires VISION_INFINIE_BASE_URL and VISION_INFINIE_MODEL.")
        return OpenAICompatibleProvider(base_url=base_url, model=model)
    raise ValueError("Unsupported VISION_INFINIE_PROVIDER. Choose local or openai-compatible.")
