"""Role boundaries and approval routing for VISION INFINIE.

This module enforces communication routing and approval policy at application
level. It does not authenticate the caller; production identity verification
must be supplied by a trusted authentication layer.
"""
from dataclasses import dataclass
from enum import Enum


class Role(str, Enum):
    FOUNDER = "founder"
    DIRECTOR = "director"
    AGENT = "agent"


class Decision(str, Enum):
    ALLOW = "allow"
    REQUIRE_FOUNDER = "require_founder"
    DENY = "deny"


@dataclass(frozen=True)
class AuthorizationResult:
    decision: Decision
    approver: Role | None
    reason: str


# Only actions explicitly delegated here may be approved by the Director.
# Unknown actions are reserved for the Founder.
DIRECTOR_DELEGATED_ACTIONS = frozenset({
    "assign_agent_task",
    "read_project_non_sensitive_data",
    "run_local_tests",
    "prepare_draft",
})


def can_route_message(sender: Role, recipient: Role) -> bool:
    """Return whether a message may pass along the management chain."""
    allowed_routes = {
        (Role.FOUNDER, Role.DIRECTOR),
        (Role.DIRECTOR, Role.FOUNDER),  # escalation / reporting only
        (Role.DIRECTOR, Role.AGENT),
        (Role.AGENT, Role.DIRECTOR),
    }
    return (sender, recipient) in allowed_routes


def authorize_action(
    requester: Role,
    action: str,
    *,
    director_approved: bool = False,
    founder_approved: bool = False,
) -> AuthorizationResult:
    """Evaluate approval state; this function never performs the action."""
    if not action or not action.strip():
        raise ValueError("Action is required.")

    if requester == Role.FOUNDER:
        return AuthorizationResult(Decision.ALLOW, Role.FOUNDER,
                                  "Founder initiated the action.")

    if requester == Role.AGENT:
        if not director_approved:
            return AuthorizationResult(Decision.DENY, Role.DIRECTOR,
                                       "Agent must request the Director first.")
        return AuthorizationResult(Decision.ALLOW, Role.DIRECTOR,
                                   "Director approved the Agent action.")

    if requester == Role.DIRECTOR:
        if action in DIRECTOR_DELEGATED_ACTIONS:
            return AuthorizationResult(Decision.ALLOW, Role.DIRECTOR,
                                       "Action is within delegated authority.")
        if founder_approved:
            return AuthorizationResult(Decision.ALLOW, Role.FOUNDER,
                                       "Founder approved the reserved action.")
        return AuthorizationResult(Decision.REQUIRE_FOUNDER, Role.FOUNDER,
                                   "Founder approval is required.")

    return AuthorizationResult(Decision.DENY, None, "Unknown role.")
