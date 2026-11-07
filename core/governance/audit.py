"""Append-only local audit events for system traceability."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_LOG = Path(__file__).resolve().parents[2] / "data" / "audit" / "events.jsonl"


def record_event(event_type: str, detail: str, log_path: str | Path | None = None) -> dict:
    event_type, detail = event_type.strip(), detail.strip()
    if not event_type or not detail:
        raise ValueError("event_type and detail are required")
    event = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event_type": event_type,
        "detail": detail,
    }
    path = Path(log_path) if log_path is not None else DEFAULT_LOG
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(event, ensure_ascii=False) + "\n")
    return event
