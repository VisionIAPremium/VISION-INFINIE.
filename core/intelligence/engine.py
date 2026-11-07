"""Local-first knowledge engine for VISION INFINIE.
Uses only the Python standard library; this is keyword search, not a generative model.
"""
from __future__ import annotations
import json
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_STORE = Path(__file__).resolve().parents[2] / "data" / "knowledge" / "knowledge.json"

def _now() -> str:
    return datetime.now(timezone.utc).isoformat()

def _path(store_path: str | Path | None = None) -> Path:
    return Path(store_path) if store_path is not None else DEFAULT_STORE

def _read(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        raise ValueError(f"Cannot read knowledge store: {exc}") from exc
    if not isinstance(value, list):
        raise ValueError("Knowledge store must contain a JSON array.")
    return value

def _write(path: Path, entries: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(entries, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temp.replace(path)

def add_entry(title: str, content: str, tags: list[str] | None = None, store_path: str | Path | None = None) -> dict[str, Any]:
    """Validate and persist one knowledge entry."""
    title, content = title.strip(), content.strip()
    if not title:
        raise ValueError("title must not be empty")
    if not content:
        raise ValueError("content must not be empty")
    clean_tags = sorted({tag.strip() for tag in (tags or []) if tag.strip()})
    path = _path(store_path)
    entries = _read(path)
    timestamp = _now()
    entry = {"id": str(uuid.uuid4()), "title": title, "content": content, "tags": clean_tags, "created_at": timestamp, "updated_at": timestamp}
    entries.append(entry)
    _write(path, entries)
    return entry

def list_entries(store_path: str | Path | None = None) -> list[dict[str, Any]]:
    """Return all entries in insertion order."""
    return _read(_path(store_path))

def search_entries(query: str, limit: int = 10, store_path: str | Path | None = None) -> list[dict[str, Any]]:
    """Return entries ranked by deterministic keyword matches."""
    if limit < 1:
        raise ValueError("limit must be at least 1")
    terms = set(re.findall(r"[^\W_]+", query.casefold(), flags=re.UNICODE))
    if not terms:
        return []
    ranked = []
    for entry in list_entries(store_path):
        title = str(entry.get("title", "")).casefold()
        content = str(entry.get("content", "")).casefold()
        tags = " ".join(str(tag) for tag in entry.get("tags", [])).casefold()
        score = sum(3 if term in title else 2 if term in tags else 1 if term in content else 0 for term in terms)
        if score:
            ranked.append((score, entry))
    ranked.sort(key=lambda item: (-item[0], item[1].get("created_at", "")))
    return [entry for _, entry in ranked[:limit]]
