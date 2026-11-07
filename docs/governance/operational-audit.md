# Operational audit

Run the local, read-only system audit:

```bash
python cli.py audit
```

The audit checks required project files, knowledge-store JSON integrity, core module imports, provider configuration, local memory availability, audit-log structure, and Airtable connection state.

## Safety boundaries

- The audit makes no network requests.
- It does not read or print secret values.
- Airtable remains read-only; the audit never calls Airtable.
- It does not change files, records, credentials, workflows, or deployments.
- A passing audit is not a production-security certification. Authentication, authorization, backup/restore, monitoring, privacy review, rate limiting, deployment hardening, and live integration tests remain separate acceptance gates.

Exit codes: `0` when no check fails; `1` when at least one check fails.
