"""Explicit registry of the seven specialist VIP roles.

These are bounded role definitions. Registration does not launch autonomous
processes or authorize external actions.
"""
from dataclasses import dataclass

@dataclass(frozen=True)
class AgentSpec:
    name: str
    purpose: str
    capabilities: tuple[str, ...] = ()
    requires_human_approval: bool = True

DEFAULT_AGENTS = (
    AgentSpec("VIP-01", "AI Systems Architect", ("architecture_review", "technical_design")),
    AgentSpec("VIP-02", "Automation Engineer", ("workflow_design", "local_test_preparation")),
    AgentSpec("VIP-03", "Data Intelligence Manager", ("data_quality_review", "schema_analysis")),
    AgentSpec("VIP-04", "Career OS Manager", ("career_workflow_analysis", "task_planning")),
    AgentSpec("VIP-05", "Content Intelligence Manager", ("content_drafting", "content_review")),
    AgentSpec("VIP-06", "Governance Officer", ("policy_review", "permission_review")),
    AgentSpec("VIP-07", "Quality Auditor", ("test_review", "audit_reporting")),
)
_REGISTRY: dict[str, AgentSpec] = {agent.name: agent for agent in DEFAULT_AGENTS}

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
