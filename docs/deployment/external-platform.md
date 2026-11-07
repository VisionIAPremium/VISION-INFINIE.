# Deployment guide — VISION INFINIE

## Included foundation

- HMAC-SHA256 bearer tokens with subject, role, expiry, and a maximum 24-hour lifetime.
- API authorization: only Founder and Director tokens may call POST /ask.
- Seven specialist VIP role definitions are pre-registered. They are not autonomous workers.
- Docker image runs as a non-root user.
- Compose uses a read-only root filesystem, drops Linux capabilities, enables no-new-privileges, and persists application data.
- Compose binds host port 8765 to 127.0.0.1 only.
- GET /health is available for local health checks.

## Local container launch

1. Install Docker Engine and Docker Compose.
2. Copy .env.example to .env.
3. Replace VISION_INFINIE_TOKEN_SECRET with a unique random secret of at least 32 characters.
4. Run: python -m unittest discover -s tests -v
5. Run: docker compose up --build -d
6. Check: curl http://127.0.0.1:8765/health
7. Logs: docker compose logs --tail=100 vision-infinie

## Issue a service token

Set the same signing secret in the CLI environment. Example:

```bash
VISION_INFINIE_TOKEN_SECRET='YOUR_SECRET_FROM_SECRET_MANAGER' python cli.py issue-token --subject founder-console --role founder --ttl 3600
```

The CLI prints a bearer token. Store it in a secure client-side secret store. Never put it in source control, browser code, a URL, or logs. Changing the signing secret invalidates all outstanding tokens.

Example request:

```bash
curl -X POST http://127.0.0.1:8765/ask \
  -H 'Authorization: Bearer YOUR_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{"question":"Présente l’architecture de VISION INFINIE."}'
```

## Public deployment acceptance gates

The included container is an application service, not a complete public production stack. Before internet exposure:

- Place it behind a maintained reverse proxy or ingress that enforces HTTPS/TLS.
- Configure DNS, certificates, firewall, and edge security policies.
- Store secrets in a managed secret store; never commit production secrets.
- Add centralized identity management (OIDC), MFA, token revocation, rate limiting, monitoring, and alerting.
- Validate backup and restore, data retention, privacy, and incident response.
- Add a production database before multi-user or business-critical use.
- Run dependency, container, penetration, and privacy reviews.
- Configure external AI and Airtable only after provider selection, scoped credentials, cost limits, and integration tests.

## Explicit limitations

The HMAC token is an internal service-token mechanism, not OAuth/OIDC, MFA, user account management, or token revocation. The VIP registry describes roles but does not launch agent processes. The default AI provider is offline/context-only. No external account, paid resource, integration, public DNS, or production deployment is activated by this repository change.
