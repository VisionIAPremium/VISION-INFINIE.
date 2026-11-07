"""Read-only operational audit for the VISION INFINIE repository."""
from __future__ import annotations

import importlib
import json
import os
import sys
from pathlib import Path
from typing import Any


REQUIRED_FILES = (
    "app.py",
    "cli.py",
    "core/ai/config.py",
    "core/ai/orchestrator.py",
    "core/ai/provider.py",
    "core/director/director.py",
    "core/governance/authority.py",
    "core/governance/audit.py",
    "core/integrations/airtable/client.py",
    "core/intelligence/engine.py",
    "core/memory/store.py",
    ".github/workflows/python-tests.yml",
)

REQUIRED_MODULES = (
    "core.ai.config",
    "core.ai.orchestrator",
    "core.director.director",
    "core.governance.authority",
    "core.integrations.airtable.client",
    "core.intelligence.engine",
    "core.memory.store",
)


def _check(name: str, status: str, detail: str) -> dict[str, str]:
    return {"name": name, "status": status, "detail": detail}


def run_audit(root: str | Path | None = None) -> dict[str, Any]:
    """Inspect local project readiness without network calls or mutations."""
    base = Path(root) if root is not None else Path(__file__).resolve().parents[2]
    checks: list[dict[str, str]] = []

    missing = [item for item in REQUIRED_FILES if not (base / item).is_file()]
    checks.append(_check(
        "project_structure",
        "PASS" if not missing else "FAIL",
        "Required project files are present." if not missing
        else "Missing files: " + ", ".join(missing),
    ))

    knowledge_path = base / "data" / "knowledge" / "knowledge.json"
    try:
        payload = json.loads(knowledge_path.read_text(encoding="utf-8"))
        valid = isinstance(payload, list)
        checks.append(_check(
            "knowledge_store",
            "PASS" if valid else "FAIL",
            f"Valid JSON knowledge list ({len(payload)} entries)." if valid
            else "Knowledge store must contain a JSON list.",
        ))
    except FileNotFoundError:
        checks.append(_check("knowledge_store", "FAIL", "Knowledge store is missing."))
    except (OSError, json.JSONDecodeError) as exc:
        checks.append(_check("knowledge_store", "FAIL", f"Knowledge store cannot be read: {type(exc).__name__}."))

    import_errors = []
    for module in REQUIRED_MODULES:
        try:
            importlib.import_module(module)
        except Exception as exc:  # audit reports the exception class, never secrets
            import_errors.append(f"{module} ({type(exc).__name__})")
    checks.append(_check(
        "module_imports",
        "PASS" if not import_errors else "FAIL",
        "Core modules import successfully." if not import_errors
        else "Import errors: " + ", ".join(import_errors),
    ))

    provider = os.getenv("VISION_INFINIE_PROVIDER", "local").strip().lower()
    if provider == "local":
        checks.append(_check("ai_provider", "PASS", "Offline provider selected; no remote model call is enabled."))
    elif provider == "openai-compatible":
        missing_config = [
            key for key in ("VISION_INFINIE_BASE_URL", "VISION_INFINIE_MODEL", "VISION_INFINIE_API_KEY")
            if not os.getenv(key)
        ]
        checks.append(_check(
            "ai_provider",
            "PASS" if not missing_config else "WARN",
            "Remote provider configuration is present; this audit did not make a live request."
            if not missing_config else "Remote provider is selected but configuration is incomplete: " + ", ".join(missing_config),
        ))
    else:
        checks.append(_check("ai_provider", "FAIL", "Unsupported provider selection."))

    memory_path = base / "data" / "memory" / "memory.sqlite3"
    checks.append(_check(
        "memory_store",
        "PASS" if memory_path.is_file() else "WARN",
        "Local memory database exists." if memory_path.is_file()
        else "Memory database will be created on first authorized memory operation.",
    ))

    audit_path = base / "data" / "audit" / "events.jsonl"
    if not audit_path.exists():
        checks.append(_check("audit_log", "WARN", "No audit events recorded yet."))
    else:
        malformed = 0
        try:
            for line in audit_path.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    try:
                        event = json.loads(line)
                        if not isinstance(event, dict) or not {"timestamp", "event_type", "detail"} <= event.keys():
                            malformed += 1
                    except json.JSONDecodeError:
                        malformed += 1
            checks.append(_check(
                "audit_log",
                "PASS" if malformed == 0 else "FAIL",
                "Append-only audit log is structurally valid." if malformed == 0
                else f"{malformed} malformed audit event(s) detected.",
            ))
        except OSError:
            checks.append(_check("audit_log", "FAIL", "Audit log cannot be read."))

    # Presence is reported only as a boolean; secret values are never read into output.
    airtable_configured = bool(os.getenv("AIRTABLE_BASE_ID") and os.getenv("AIRTABLE_TOKEN"))
    checks.append(_check(
        "airtable_integration",
        "WARN" if airtable_configured else "PASS",
        "Credentials detected; integration remains read-only and no request was made."
        if airtable_configured else "Not connected; read-only adapter is available but inactive.",
    ))

    counts = {state: sum(1 for item in checks if item["status"] == state) for state in ("PASS", "WARN", "FAIL")}
    overall = "FAIL" if counts["FAIL"] else ("READY_WITH_WARNINGS" if counts["WARN"] else "READY")
    return {
        "system": "VISION INFINIE",
        "audit_mode": "READ_ONLY",
        "python": sys.version.split()[0],
        "overall_status": overall,
        "summary": counts,
        "checks": checks,
        "limitations": [
            "No network request or external integration was executed.",
            "This audit does not prove production security, authentication, deployment, or live provider availability.",
        ],
    }
