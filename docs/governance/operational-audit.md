# Operational audit

Run the local read-only audit:

```bash
python cli.py audit
```

The audit checks required source and container files, knowledge-store JSON integrity, core module imports, AI provider configuration, API signing-secret presence, the seven specialist VIP role definitions, local memory availability, audit-log structure, and Airtable configuration presence.

## Safety boundaries

- The audit makes no network requests.
- It does not print secret values.
- Airtable remains inactive/read-only; the audit never calls Airtable.
- It does not change files, records, credentials, workflows, or deployments.
- Missing API signing secret is reported as a warning, not a test failure, so CI can run without production secrets.
- A passing audit is not a production-security certification. TLS, identity-provider integration, token revocation, backups, monitoring, privacy review, rate limiting, and live integration tests remain separate acceptance gates.

Exit codes: 0 when no check fails; 1 when at least one check fails.
