# VISION INFINIE

**Intelligent Systems & AI Automation Platform**

Technical foundation of VISION IA PREMIUM.

## Current capabilities

- **Knowledge:** local JSON knowledge base with deterministic keyword retrieval.
- **Memory:** persistent SQLite memory store, populated only through explicit application calls.
- **AI Core:** orchestrates knowledge retrieval, optional memory context, and a provider adapter.
- **Providers:** offline context-only provider by default; optional OpenAI-compatible HTTP adapter configured through environment variables.
- **Decision Engine:** explainable rule evaluation.
- **Agent Registry:** explicit agent definitions.
- **Automation Gate:** proposals require human approval; this module does not execute external actions.
- **CLI:** add/search/list knowledge, save memory, and ask the local AI Core.
- **CI:** GitHub Actions runs unit tests on pushes and pull requests.

## Important capability boundary

The default provider is **not a generative AI model**. It returns relevant local source excerpts and explicitly reports when no context is found. To use a remote model, configure `VISION_INFINIE_API_KEY`, an API-compatible base URL, and a model in the application integration. No credential is committed to this repository.

## Project structure

```text
.
├── cli.py
├── core/
│   ├── ai/              # provider adapters and orchestrator
│   ├── intelligence/   # knowledge retrieval
│   ├── memory/         # SQLite memory
│   ├── decision/
│   ├── agents/
│   └── automation/
├── data/
├── docs/
├── tests/
└── .github/workflows/
```

## Requirements and local use

Python 3.10+, standard library only.

```bash
python -m unittest discover -s tests -v
python cli.py add --title "Vision" --content "Build governed intelligent systems." --tag strategy
python cli.py remember "The project follows a modular architecture."
python cli.py ask "What is the project architecture?"
python cli.py search "intelligent systems"
```

The knowledge base is stored in `data/knowledge/knowledge.json`; local memory is stored in `data/memory/memory.sqlite3`. Do not store secrets or sensitive personal data.

## Governance

- No remote model request occurs unless the remote provider is explicitly configured and called.
- API credentials are read from environment variables, never hard-coded.
- Retrieved context is supplied to the model as context, not trusted as executable instructions.
- Automation proposals do not trigger external actions.
- Production deployment still requires authentication, authorization, backup/restore, monitoring, privacy review, rate limits, and security testing.

## Roadmap

1. Complete and verify the local AI Core.
2. Configure and test a selected model provider.
3. Add provenance, memory retention controls, and audit logs.
4. Add bounded agent orchestration.
5. Build a secure web interface and deployment pipeline.
