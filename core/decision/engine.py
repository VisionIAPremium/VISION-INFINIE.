"""Explainable rule-based decision engine."""
from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class Decision:
    outcome: str
    reasons: tuple[str, ...]

def evaluate(required_checks: dict[str, bool]) -> Decision:
    """Approve only when at least one check exists and every check passes."""
    if not required_checks:
        return Decision("needs_review", ("No checks supplied; human review required.",))
    failed = tuple(name for name, passed in required_checks.items() if not passed)
    if failed:
        return Decision("needs_review", tuple(f"Check failed: {name}" for name in failed))
    return Decision("eligible", ("All supplied checks passed.",))
