"""Minimal, explicit agent registry with safe default permissions."""
from dataclasses import dataclass

@dataclass(frozen=True)
class AgentSpec:
    name: str
    purpose: str
    capabilities: tuple[str, ...] = ()
    requires_human_approval: bool = True

_REGISTRY: dict[str, AgentSpec] = {}

def register_agent(spec: AgentSpec) -> None:
    if not spec.name.strip() or not spec.purpose.strip():
        raise ValueError("Agent name and purpose are required.")
    if spec.name in _REGISTRY:
        raise ValueError(f"Agent already registered: {spec.name}")
    _REGISTRY[spec.name] = spec

def list_agents() -> list[AgentSpec]:
    return sorted(_REGISTRY.values(), key=lambda item: item.name.casefold())

def get_agent(name: str) -> AgentSpec | None:
    return _REGISTRY.get(name)
