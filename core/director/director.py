"""Central Director: sole interface between the Founder and agent modules."""
from __future__ import annotations

from dataclasses import dataclass
from uuid import uuid4

from core.ai.orchestrator import AICore
from core.agents.registry import get_agent
from core.governance.audit import record_event
from core.governance.authority import Decision, Role, authorize_action


@dataclass(frozen=True)
class AgentTask:
    task_id: str
    agent_name: str
    instruction: str
    status: str = "assigned"


@dataclass(frozen=True)
class AgentReport:
    task_id: str
    agent_name: str
    report: str


class Director:
    """Receives Founder instructions and mediates all agent work.

    This application service does not authenticate identities or execute
    external integrations. Callers must be authenticated by a trusted layer
    before invoking Founder-only methods in a deployed system.
    """

    def __init__(self, ai_core: AICore | None = None):
        self.ai_core = ai_core or AICore()
        self._tasks: dict[str, AgentTask] = {}
        self._reports: dict[str, AgentReport] = {}

    def receive_founder_instruction(self, instruction: str) -> dict:
        instruction = instruction.strip()
        if not instruction:
            raise ValueError("Founder instruction must not be empty.")
        record_event("director.founder_instruction", "Instruction received by Director.")
        result = self.ai_core.ask(instruction)
        record_event("director.founder_response_prepared", "Director prepared a response for Founder.")
        return {
            "channel": "director_to_founder",
            "answer": result["answer"],
            "provider": result["provider"],
            "knowledge_hits": result["knowledge_hits"],
            "memory_hits": result["memory_hits"],
        }

    def assign_agent_task(self, agent_name: str, instruction: str) -> AgentTask:
        instruction = instruction.strip()
        agent = get_agent(agent_name)
        if agent is None:
            raise ValueError(f"Unknown agent: {agent_name}")
        if not instruction:
            raise ValueError("Agent instruction must not be empty.")
        auth = authorize_action(Role.DIRECTOR, "assign_agent_task")
        if auth.decision != Decision.ALLOW:
            raise PermissionError(auth.reason)
        task = AgentTask(str(uuid4()), agent_name, instruction)
        self._tasks[task.task_id] = task
        record_event("director.agent_task_assigned", f"Task {task.task_id} assigned to {agent_name}.")
        return task

    def receive_agent_report(self, report: AgentReport) -> None:
        task = self._tasks.get(report.task_id)
        if task is None or task.agent_name != report.agent_name:
            raise ValueError("Report does not match a task assigned by the Director.")
        if not report.report.strip():
            raise ValueError("Agent report must not be empty.")
        self._reports[report.task_id] = report
        record_event("director.agent_report_received", f"Report received for task {report.task_id}.")

    def prepare_founder_briefing(self, task_id: str) -> dict:
        task = self._tasks.get(task_id)
        report = self._reports.get(task_id)
        if task is None or report is None:
            raise ValueError("The Director needs a matching agent report before briefing the Founder.")
        return {
            "channel": "director_to_founder",
            "task_id": task_id,
            "agent": task.agent_name,
            "instruction": task.instruction,
            "report": report.report,
            "review_status": "received_by_director_not_independently_verified",
        }


__all__ = ["Director", "AgentTask", "AgentReport"]