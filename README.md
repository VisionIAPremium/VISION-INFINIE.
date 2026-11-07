# VISION INFINIE

**Intelligent Systems & AI Automation Platform**

Technical foundation of VISION IA PREMIUM.

## Current capabilities

- **Knowledge:** local JSON knowledge base with deterministic keyword retrieval.
- **Memory:** persistent SQLite memory store, populated only through explicit application calls.
- **AI Core:** orchestrates knowledge retrieval, optional memory context, and a model-provider adapter.
- **Providers:** offline context-only provider by default; optional OpenAI-compatible HTTP adapter configured through environment variables.
- **Decision Engine:** explainable rule evaluation.
- **Agent Registry:** explicit agent definitions.
- **Automation Gate:** proposals require human approval; this module does not execute external actions.
- **Governance:** append-only local JSONL audit events.
- **Local API:** HTTP health and question endpoints bound to 127.0.0.1 only.
- **CLI and CI:** local commands plus GitHub Actions unit tests.

## Capability boundary

The default provider is **not a generative AI model**. It returns relevant local source excerpts and reports when no context is found. A remote model adapter exists but must be explicitly configured with an API-compatible endpoint, model, and `VISION_INFINIE_API_KEY`. No credential is committed.

## Configure a model provider

The default provider remains offline. To select the optional OpenAI-compatible adapter, set these environment variables in the runtime environment:

    VISION_INFINIE_PROVIDER=openai-compatible
    VISION_INFINIE_BASE_URL=https://api.example.com/v1
    VISION_INFINIE_MODEL=your-model-name
    VISION_INFINIE_API_KEY=your-secret-key

Use the exact endpoint and model identifier supplied by your provider. Never commit the API key or paste it into chat. Set `VISION_INFINIE_PROVIDER=local` to use the offline provider. The application selects the provider through `core/ai/config.py`.

Automated provider tests mock the HTTP response; they validate request construction, response parsing, configuration, and missing-key handling without making a paid external API call. A live provider test still requires valid provider credentials and is not claimed by CI.

See `docs/ai/provider-configuration.md` for details.
## Structure

```text
.
├── app.py
├── cli.py
├── core/
│   ├── ai/              # provider adapters and orchestrator
│   ├── intelligence/   # knowledge retrieval
│   ├── memory/         # SQLite memory
│   ├── decision/
│   ├── agents/
│   ├── automation/
│   └── governance/     # audit log
├── data/
├── docs/
├── tests/
└── .github/workflows/
```

## Run locally

Requires Python 3.10+; current foundation uses only the standard library.

```bash
python -m unittest discover -s tests -v
python cli.py add --title "Vision" --content "Build governed intelligent systems." --tag strategy
python cli.py remember "The project follows a modular architecture."
python cli.py ask "What is the project architecture?"
python cli.py search "intelligent systems"
python app.py
```

The local API listens at `http://127.0.0.1:8765`. Check it with `GET /health`; ask a question with `POST /ask` and JSON body `{"question":"What is VISION INFINIE?"}`. It is intentionally bound to localhost and must not be exposed publicly as-is.

The knowledge base is stored in `data/knowledge/knowledge.json`; local memory in `data/memory/memory.sqlite3`; audit events in `data/audit/events.jsonl`. Do not store secrets or sensitive personal data.

## Governance authority

The project follows the [Triangle of Authority](docs/governance/triangle-of-authority.md): the Founder communicates with the Director only; Agents report to and receive instructions from the Director only. Agents have no direct communication route to the Founder. The Director handles delegated operations and escalates reserved decisions to the Founder. The application-level routing and approval rules are implemented in `core/governance/authority.py` and tested in `tests/test_authority.py`. These checks do not authenticate identities; production deployment requires a trusted authentication layer.

## Governance and production limits

- No remote model request occurs unless a remote provider is explicitly configured and invoked.
- API credentials are read from environment variables, never hard-coded.
- Retrieved context is data, not executable instructions.
- Automation proposals do not trigger external actions.
- The local API has no user authentication and must remain on localhost.
- Production deployment still requires authentication, authorization, backup/restore, monitoring, privacy review, rate limits, security testing, and infrastructure configuration.

## Roadmap

1. Validate the local AI Core and API through CI.
2. Configure and test a selected model provider.
3. Add source provenance, memory retention controls, and audit review tools.
4. Add bounded agent orchestration and integration adapters.
5. Build a secure web interface and deployment pipeline.
