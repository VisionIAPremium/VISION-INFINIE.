"""Provider adapters for the VISION INFINIE AI Core.

The local provider is deterministic and does not call a model. The remote
adapter uses an OpenAI-compatible chat-completions endpoint only when explicitly
configured and invoked by the application.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Protocol
from urllib.request import Request, urlopen


class ModelProvider(Protocol):
    def generate(self, prompt: str, context: list[dict], system_instruction: str) -> str: ...


@dataclass
class LocalContextProvider:
    """Safe offline fallback: returns retrieved source excerpts, not generated facts."""

    max_chars: int = 1800

    def generate(self, prompt: str, context: list[dict], system_instruction: str = "") -> str:
        if not context:
            return "Je ne trouve aucun élément dans la base de connaissances locale pour répondre. Ajoute des sources ou configure un fournisseur IA."
        excerpts = []
        remaining = self.max_chars
        for item in context:
            title = str(item.get("title", "Sans titre"))
            body = str(item.get("content", ""))
            excerpt = f"- {title}: {body}"[:remaining]
            excerpts.append(excerpt)
            remaining -= len(excerpt)
            if remaining <= 0:
                break
        return "Réponse locale fondée uniquement sur les éléments retrouvés :\n" + "\n".join(excerpts)


@dataclass
class OpenAICompatibleProvider:
    """Optional remote provider. Credentials are read only from environment."""

    base_url: str
    model: str
    api_key_env: str = "VISION_INFINIE_API_KEY"
    timeout_seconds: int = 30

    def generate(self, prompt: str, context: list[dict], system_instruction: str = "") -> str:
        api_key = os.getenv(self.api_key_env)
        if not api_key:
            raise RuntimeError(f"Missing API key environment variable: {self.api_key_env}")
        messages = [
            {"role": "system", "content": system_instruction or "Answer accurately. Use supplied context and state uncertainty."},
            {"role": "user", "content": "Context:\n" + json.dumps(context, ensure_ascii=False) + "\n\nQuestion:\n" + prompt},
        ]
        payload = json.dumps({"model": self.model, "messages": messages, "temperature": 0.2}).encode("utf-8")
        url = self.base_url.rstrip("/") + "/chat/completions"
        request = Request(url, data=payload, headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }, method="POST")
        try:
            with urlopen(request, timeout=self.timeout_seconds) as response:
                result = json.loads(response.read().decode("utf-8"))
        except Exception as exc:
            raise RuntimeError(f"AI provider request failed: {exc}") from exc
        try:
            return result["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise RuntimeError("AI provider returned an unexpected response format.") from exc
