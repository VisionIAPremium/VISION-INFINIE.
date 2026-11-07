"""Read-only operational and deployment audit for VISION INFINIE."""
from __future__ import annotations
import importlib, json, os, sys
from pathlib import Path
from typing import Any

REQUIRED_FILES = (
    "app.py", "cli.py", "core/ai/config.py", "core/ai/orchestrator.py",
    "core/ai/provider.py", "core/director/director.py", "core/governance/authority.py",
    "core/governance/auth.py", "core/governance/audit.py",
    "core/integrations/airtable/client.py", "core/intelligence/engine.py",
    "core/memory/store.py", ".github/workflows/python-tests.yml",
    "Dockerfile", "docker-compose.yml", ".env.example",
)
REQUIRED_MODULES = (
    "core.ai.config", "core.ai.orchestrator", "core.director.director",
    "core.governance.authority", "core.governance.auth",
    "core.integrations.airtable.client", "core.intelligence.engine", "core.memory.store",
)

def _check(name: str, status: str, detail: str) -> dict[str, str]:
    return {"name": name, "status": status, "detail": detail}

def run_audit(root: str | Path | None = None) -> dict[str, Any]:
    """Inspect project readiness without network calls or mutations."""
    base = Path(root) if root is not None else Path(__file__).resolve().parents[2]
    checks = []
    missing = [item for item in REQUIRED_FILES if not (base / item).is_file()]
    checks.append(_check("project_structure", "PASS" if not missing else "FAIL",
        "Required project and deployment files are present." if not missing else "Missing files: " + ", ".join(missing)))
    knowledge_path = base / "data" / "knowledge" / "knowledge.json"
    try:
        payload = json.loads(knowledge_path.read_text(encoding="utf-8"))
        valid = isinstance(payload, list)
        checks.append(_check("knowledge_store", "PASS" if valid else "FAIL",
            f"Valid JSON knowledge list ({len(payload)} entries)." if valid else "Knowledge store must contain a JSON list."))
    except FileNotFoundError:
        checks.append(_check("knowledge_store", "FAIL", "Knowledge store is missing."))
    except (OSError, json.JSONDecodeError) as exc:
        checks.append(_check("knowledge_store", "FAIL", f"Knowledge store cannot be read: {type(exc).__name__}."))
    errors = []
    for module in REQUIRED_MODULES:
        try:
            importlib.import_module(module)
        except Exception as exc:
            errors.append(f"{module} ({type(exc).__name__})")
    checks.append(_check("module_imports", "PASS" if not errors else "FAIL",
        "Core modules import successfully." if not errors else "Import errors: " + ", ".join(errors)))
    provider = os.getenv("VISION_INFINIE_PROVIDER", "local").strip().lower()
    if provider == "local":
        checks.append(_check("ai_provider", "PASS", "Offline context provider selected; no remote model call enabled."))
    elif provider == "openai-compatible":
        missing_config = [key for key in ("VISION_INFINIE_BASE_URL", "VISION_INFINIE_MODEL", "VISION_INFINIE_API_KEY") if not os.getenv(key)]
        checks.append(_check("ai_provider", "PASS" if not missing_config else "WARN",
            "Remote provider configuration present; no live request was made." if not missing_config
            else "Remote provider configuration incomplete: " + ", ".join(missing_config)))
    else:
        checks.append(_check("ai_provider", "FAIL", "Unsupported provider selection."))
    secret = os.getenv("VISION_INFINIE_TOKEN_SECRET", "")
    strong_secret = len(secret.encode("utf-8")) >= 32
    checks.append(_check("api_authentication", "PASS" if strong_secret else "WARN",
        "Token signing secret configured." if strong_secret else "Set a unique VISION_INFINIE_TOKEN_SECRET of at least 32 characters before API use."))
    from core.agents.registry import list_agents
    count = len(list_agents())
    checks.append(_check("vip_agent_registry", "PASS" if count == 7 else "FAIL",
        f"{count} specialist VIP roles registered." if count == 7 else f"Expected 7 specialist VIP roles; found {count}."))
    memory_path = base / "data" / "memory" / "memory.sqlite3"
    checks.append(_check("memory_store", "PASS" if memory_path.is_file() else "WARN",
        "Local memory database exists." if memory_path.is_file() else "Memory database is created on first authorized memory operation."))
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
            checks.append(_check("audit_log", "PASS" if malformed == 0 else "FAIL",
                "Audit log is structurally valid." if malformed == 0 else f"{malformed} malformed events detected."))
        except OSError:
            checks.append(_check("audit_log", "FAIL", "Audit log cannot be read."))
    airtable = bool(os.getenv("AIRTABLE_BASE_ID") and os.getenv("AIRTABLE_TOKEN"))
    checks.append(_check("airtable_integration", "WARN" if airtable else "PASS",
        "Credentials detected; no request was made." if airtable else "Inactive; read-only adapter available."))
    summary = {state: sum(1 for item in checks if item["status"] == state) for state in ("PASS", "WARN", "FAIL")}
    overall = "FAIL" if summary["FAIL"] else ("READY_WITH_WARNINGS" if summary["WARN"] else "READY")
    return {"system": "VISION INFINIE", "audit_mode": "READ_ONLY", "python": sys.version.split()[0],
        "overall_status": overall, "summary": summary, "checks": checks,
        "limitations": ["No network request or external integration was executed.",
            "This audit does not certify public deployment, TLS, external identity provider, backups, or live model availability."]}
