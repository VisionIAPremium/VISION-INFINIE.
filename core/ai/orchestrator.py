"""Coordinates retrieval, optional memory, and a model provider."""
from __future__ import annotations

from core.intelligence.engine import search_entries
from core.ai.config import build_provider
from core.ai.provider import ModelProvider
from core.memory.store import MemoryStore


class AICore:
    def __init__(self, provider: ModelProvider | None = None, memory: MemoryStore | None = None):
        self.provider = provider if provider is not None else build_provider()
        self.memory = memory

    def ask(self, question: str, knowledge_limit: int = 5, memory_limit: int = 3) -> dict:
        question = question.strip()
        if not question:
            raise ValueError("Question must not be empty.")
        knowledge = search_entries(question, limit=knowledge_limit)
        memories = self.memory.search(question, limit=memory_limit) if self.memory else []
        context = list(knowledge) + [
            {"title": "Mémoire locale", "content": item["content"], "id": item["id"]}
            for item in memories
        ]
        answer = self.provider.generate(
            prompt=question,
            context=context,
            system_instruction=(
                "Tu es le moteur d'intelligence de VISION INFINIE. "
                "Distingue les faits du contexte, n'invente pas les sources et indique les limites."
            ),
        )
        return {"answer": answer, "knowledge_hits": len(knowledge), "memory_hits": len(memories), "provider": type(self.provider).__name__}
