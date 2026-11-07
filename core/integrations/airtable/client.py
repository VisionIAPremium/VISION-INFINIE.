"""Read-only Airtable REST client for VISION INFINIE.

No credentials are stored in source. The token is read from AIRTABLE_TOKEN
only when a request is made. This client intentionally exposes no write API.
"""
from __future__ import annotations

import json
import os
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen


class AirtableConfigurationError(RuntimeError):
    pass


class AirtableAPIError(RuntimeError):
    pass


class AirtableReadOnlyClient:
    """Minimal read-only client for the Airtable Web API."""

    def __init__(
        self,
        base_id: str | None = None,
        *,
        token: str | None = None,
        timeout: float = 15.0,
    ) -> None:
        self.base_id = base_id or os.getenv("AIRTABLE_BASE_ID")
        self._token = token
        self.timeout = timeout

    def _get_token(self) -> str:
        token = self._token or os.getenv("AIRTABLE_TOKEN")
        if not token:
            raise AirtableConfigurationError(
                "AIRTABLE_TOKEN is required; configure it outside the repository."
            )
        return token

    def _get_json(self, url: str) -> dict[str, Any]:
        request = Request(
            url,
            headers={
                "Authorization": f"Bearer {self._get_token()}",
                "Accept": "application/json",
                "User-Agent": "VISION-INFINIE/airtable-readonly",
            },
            method="GET",
        )
        try:
            with urlopen(request, timeout=self.timeout) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            raise AirtableAPIError(f"Airtable returned HTTP {exc.code}.") from exc
        except URLError as exc:
            raise AirtableAPIError("Airtable request could not be completed.") from exc
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise AirtableAPIError("Airtable returned an invalid JSON response.") from exc

        if not isinstance(payload, dict):
            raise AirtableAPIError("Airtable response must be a JSON object.")
        return payload

    def list_records(
        self,
        table: str,
        *,
        page_size: int = 100,
        max_pages: int = 1,
        view: str | None = None,
    ) -> list[dict[str, Any]]:
        """Read records only. Pagination is bounded to prevent unbounded scans."""
        if not self.base_id:
            raise AirtableConfigurationError("AIRTABLE_BASE_ID is required.")
        if not table or not table.strip():
            raise ValueError("A table name or ID is required.")
        if not 1 <= page_size <= 100:
            raise ValueError("page_size must be between 1 and 100.")
        if not 1 <= max_pages <= 10:
            raise ValueError("max_pages must be between 1 and 10.")

        table_path = quote(table.strip(), safe="")
        url = f"https://api.airtable.com/v0/{self.base_id}/{table_path}"
        params: dict[str, str] = {"pageSize": str(page_size)}
        if view:
            params["view"] = view

        records: list[dict[str, Any]] = []
        for _ in range(max_pages):
            response = self._get_json(f"{url}?{urlencode(params)}")
            batch = response.get("records", [])
            if not isinstance(batch, list):
                raise AirtableAPIError("Airtable records payload is invalid.")
            records.extend(item for item in batch if isinstance(item, dict))
            offset = response.get("offset")
            if not offset:
                break
            params["offset"] = str(offset)
        return records


__all__ = [
    "AirtableAPIError",
    "AirtableConfigurationError",
    "AirtableReadOnlyClient",
]
