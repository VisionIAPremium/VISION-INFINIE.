"""Human-gated automation proposal queue; never executes external actions."""
from dataclasses import dataclass
from uuid import uuid4

@dataclass(frozen=True)
class ActionProposal:
    proposal_id: str
    description: str
    status: str

def propose_action(description: str) -> ActionProposal:
    description = description.strip()
    if not description:
        raise ValueError("Action description is required.")
    return ActionProposal(str(uuid4()), description, "pending_human_approval")

def authorize_action(proposal: ActionProposal, approved: bool) -> ActionProposal:
    """Record an approval decision; does not execute the action."""
    if proposal.status != "pending_human_approval":
        raise ValueError("Only pending proposals can receive a decision.")
    status = "approved_for_manual_execution" if approved else "rejected"
    return ActionProposal(proposal.proposal_id, proposal.description, status)
