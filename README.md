# VISION INFINIE

**Intelligent Systems & AI Automation Platform**  
Technical foundation of VISION IA PREMIUM.

## Platform capabilities

- Local knowledge retrieval and persistent SQLite memory.
- AI provider adapter: offline/context-only by default; optional OpenAI-compatible provider.
- Central Director service and seven pre-registered specialist VIP role definitions.
- Human approval gate for proposed external actions.
- HMAC-SHA256 bearer-token authentication for the HTTP API.
- Role-based API access: Founder and Director can use `POST /ask`; Agent tokens are denied.
- Docker deployment foundation with non-root runtime, read-only container filesystem, persistent data volume, and localhost-only host binding.
- Read-only operational audit and GitHub Actions tests.

## Important capability boundaries

The local provider is not a generative model. It returns retrieved source context. The remote model adapter is optional and requires explicit provider configuration and a live test.

The VIP registry contains bounded role definitions, not autonomous workers. The Director is an application service, not a live ChatGPT connector or message bus. The HMAC service tokens are not a full OAuth/OIDC identity provider: no MFA, user directory, or individual token revocation is provided.

The included Compose file is intentionally bound to `127.0.0.1`. Public hosting requires a TLS reverse proxy, managed secrets, firewall/DNS configuration, monitoring, backups, rate limiting, identity management, and security review. Do not expose the application port directly to the internet.

## Run locally

Requires Python 3.10+; the application currently uses only the Python standard library.

```bash
python -m unittest discover -s tests -v
python cli.py audit
python cli.py add --title "Vision" --content "Build governed intelligent systems." --tag strategy
python cli.py remember "The project follows a modular architecture."
python cli.py ask "What is the project architecture?"
python cli.py search "intelligent systems"
python app.py
```

For the local API, configure a unique signing secret of at least 32 characters in `VISION_INFINIE_TOKEN_SECRET`. Issue a short-lived Founder token:

```bash
VISION_INFINIE_TOKEN_SECRET='YOUR_SECRET' python cli.py issue-token --subject founder-console --role founder --ttl 3600
```

Then call the authenticated endpoint:

```bash
curl -X POST http://127.0.0.1:8765/ask \
  -H 'Authorization: Bearer YOUR_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{"question":"What is VISION INFINIE?"}'
```

Health check: `GET http://127.0.0.1:8765/health`.

## Container deployment

Copy `.env.example` to `.env`, set a unique `VISION_INFINIE_TOKEN_SECRET`, then run:

```bash
docker compose up --build -d
docker compose logs --tail=100 vision-infinie
```

Detailed instructions and production acceptance gates: [External platform deployment](docs/deployment/external-platform.md).

## Governance

The project follows the [Triangle of Authority](docs/governance/triangle-of-authority.md): Founder → Director → Agents. The policy module in `core/governance/authority.py` evaluates application-level roles; token verification is implemented separately in `core/governance/auth.py`.

Airtable remains an optional bounded read-only adapter. No Airtable records, schema, or external services are modified by the application deployment template.

## Data locations

- Knowledge: `data/knowledge/knowledge.json`
- Memory: `data/memory/memory.sqlite3`
- Audit events: `data/audit/events.jsonl`

Do not store credentials or sensitive personal data in the repository, knowledge base, or logs.

## Operational audit

Run:

```bash
python cli.py audit
```

The audit checks project files, knowledge JSON, core imports, provider configuration, API signing-secret presence, VIP registry population, memory availability, audit-log structure, and Airtable configuration presence. It makes no network requests and does not print credential values. A passing audit is not a production security certification.
