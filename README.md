# VISION INFINIE

**Intelligent Systems & AI Automation Platform**

Technical foundation of VISION IA PREMIUM. Operating principles:

> Understand → Decide → Architect → Build → Test → Measure → Improve → Deploy.

## Status

The repository now contains an initial executable Python foundation. It is **not yet a complete production AI platform**: there is no LLM provider, hosted database, web interface, authentication, or deployment environment configured.

- Knowledge engine: local JSON persistence and deterministic keyword search.
- Decision engine: explainable rule evaluation.
- Agent registry: explicit agent definitions; human approval required by default.
- Automation gate: creates and approves/rejects proposals; it does not execute external actions.
- Tests: unit tests for the foundation.
- CI: GitHub Actions workflow runs the Python test suite on pushes and pull requests.

## Structure

```text
.
├── cli.py
├── core/
│   ├── intelligence/engine.py
│   ├── decision/engine.py
│   ├── agents/registry.py
│   └── automation/approval.py
├── data/knowledge/knowledge.json
├── docs/architecture/intelligence.md
├── tests/
└── .github/workflows/python-tests.yml
```

## Requirements

- Python 3.10 or newer.
- No third-party package is required for the current foundation.

## Run locally

Clone the repository, then from its root directory:

```bash
python -m unittest discover -s tests -v
python cli.py list
python cli.py add --title "VISION IA PREMIUM" --content "Build governed intelligent systems." --tag vision --tag strategy
python cli.py search "intelligent systems"
```

The knowledge store is `data/knowledge/knowledge.json`. Do not commit credentials, passwords, tokens, or sensitive personal information.

## Safety and governance

- No network calls or model calls are made by the current core.
- The automation module never performs an external action.
- Approval status means a proposal is cleared for a separately implemented manual step; it is not execution.
- Production use requires authentication, authorization, backups, monitoring, threat modelling, and deployment hardening.

## Roadmap

1. Verify the foundation through GitHub Actions.
2. Add source provenance, update/archive history, and data validation.
3. Select an AI provider and implement a bounded model adapter.
4. Add persistent agent orchestration and permission checks.
5. Add integration adapters with explicit approval gates.
6. Build the user interface, observability, security, and deployment.

See [Intelligence & Knowledge specification](docs/architecture/intelligence.md).
