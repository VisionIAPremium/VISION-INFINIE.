# Intelligence & Knowledge

## Purpose
Provide a reliable, inspectable local knowledge layer for VISION INFINIE. This first version is not a generative AI model or autonomous agent.

## Responsibilities
- Validate and store knowledge entries as UTF-8 JSON.
- Search titles, content, and tags with deterministic keyword matching.
- Return ranked results with IDs and timestamps.

## Boundaries
- Local storage only; no network calls or external actions.
- No API keys or secrets in this repository.
- Do not store sensitive personal information.

## Python interfaces
- `add_entry(title, content, tags=None, store_path=None)`
- `list_entries(store_path=None)`
- `search_entries(query, limit=10, store_path=None)`

## Validation
Run `python -m unittest discover -s tests -v`.

## Roadmap
1. Add source references and provenance.
2. Add update/archive operations with audit history.
3. Add semantic retrieval after selecting a model provider.
4. Add access control before multi-user deployment.
