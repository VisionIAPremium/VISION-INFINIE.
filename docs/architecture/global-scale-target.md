# VISION INFINIE — Global-scale target architecture

**Status:** target architecture / not deployed  
**Current implementation:** single-process Python API, local SQLite memory, local JSON knowledge, optional model adapter, Docker Compose template.

This document defines the engineering target. It does not claim that cloud infrastructure, global routing, multi-region data, or autonomous agents are already running.

## 1. Design objectives

- Secure multi-tenant service with explicit tenant and user isolation.
- Stateless application tier that can scale horizontally.
- Regional deployment with controlled data residency and disaster recovery.
- Durable asynchronous workflows with retries, idempotency, and dead-letter handling.
- Human approval for privileged, financial, external, or irreversible actions.
- Observable services with measurable availability, latency, error rate, and cost.
- Provider portability for models, storage, queues, and cloud infrastructure.

## 2. Target logical architecture

```text
Users / Web / Mobile / API clients
                |
        Global DNS + CDN + WAF
                |
       Regional API Gateway / TLS
                |
       OIDC Identity + MFA + RBAC
                |
       Stateless API / BFF layer
                |
      Central Director / Policy Engine
          /          |          \
    AI Gateway   Workflow API   Tenant Registry
       |              |
 Model providers   Durable Queue
       |              |
 Retrieval layer   Isolated Workers (VIP roles)
       |              |
 Vector index      Approval service
       |              |
 Object storage   Integration adapters
          \          /
        Managed PostgreSQL
                |
       Audit / Events / Telemetry
```

## 3. Service boundaries

| Service | Responsibility | Required controls |
|---|---|---|
| Edge | DNS, CDN, WAF, DDoS protection | TLS, rate limits, bot controls |
| Identity | Users, organizations, sessions | OIDC, MFA, recovery, revocation |
| API gateway | Routing and request policy | quotas, schema validation, request IDs |
| Tenant registry | Tenant configuration and plan | tenant-scoped authorization |
| Director | Policy, routing, orchestration | signed decisions, approval checks |
| AI gateway | Model routing and budgets | allowlists, spend limits, data controls |
| Knowledge | Documents, chunks, retrieval | provenance, tenant filters, retention |
| Memory | User-approved durable memory | consent, export, deletion, TTL |
| Workflow | Long-running tasks and state | idempotency, retries, dead-letter queue |
| VIP workers | Bounded specialist tasks | least privilege, isolated execution |
| Integration adapters | External systems | scoped credentials, read-only defaults |
| Audit | Security and business events | append-only storage, integrity controls |
| Observability | Logs, metrics, traces | redaction, alerting, SLO dashboards |

## 4. Data architecture

- **Transactional source of truth:** managed PostgreSQL with tenant identifiers, row-level security, migrations, point-in-time recovery, and tested restore.
- **Cache and coordination:** managed Redis only for ephemeral cache, rate limits, and short-lived coordination; never as the only durable task store.
- **Asynchronous execution:** managed queue with at-least-once delivery, idempotent consumers, bounded retries, and dead-letter queues.
- **Documents and artifacts:** object storage with encryption, lifecycle rules, malware scanning, and tenant-scoped access.
- **Semantic retrieval:** vector index with mandatory tenant filters and source references.
- **Audit:** append-only event pipeline with restricted write access, retention policy, and tamper-evidence.

The current SQLite and JSON stores are suitable only for local development and small single-instance operation. They are not the target multi-region persistence layer.

## 5. Global deployment strategy

### Initial production topology

Start with one EU primary region and a separate EU recovery region. Keep user data in the selected residency boundary. Use infrastructure-as-code and immutable container images. Route traffic through a global edge, but keep application writes in the primary region until consistency and failover behavior have been tested.

### Scale-out sequence

1. One production region, multiple stateless API replicas.
2. Managed database, queue, object storage, secrets manager, and centralized telemetry.
3. Worker pools scaled independently by queue depth and task class.
4. Warm recovery region with tested restore and controlled failover.
5. Read replicas and regional read routing where data policy permits.
6. Active-active only after conflict handling, idempotency, replication lag, and regional failure tests pass.

Do not introduce active-active writes merely to claim global availability.

## 6. Security baseline

- OIDC identity provider, MFA, session lifecycle, revocation, and audited administrative access.
- Tenant isolation enforced server-side on every read, write, job, and retrieval query.
- Secrets manager with rotation; no production secrets in source control or chat.
- TLS in transit and encryption at rest with managed keys.
- Least-privilege service identities and short-lived workload credentials.
- API quotas, rate limiting, payload limits, abuse detection, and WAF rules.
- Dependency, image, SAST, secret, and infrastructure scans in CI.
- Signed images, SBOM, provenance, protected branches, and required reviews.
- Data minimization, retention, export, deletion, and incident-response procedures.

## 7. Reliability objectives to ratify before launch

Initial engineering targets (proposed, not measured):

- Availability: 99.9% monthly for the public API.
- API latency: p95 under 500 ms for non-model control-plane requests.
- Async task completion: 99% within the service-class target.
- Recovery point objective: 15 minutes or better for transactional data.
- Recovery time objective: 60 minutes or better for the initial EU topology.
- No acknowledged task loss after durable queue acceptance.
- Every privileged action has an attributable audit event and approval evidence.

Model inference latency and provider outages must be measured separately from API control-plane SLOs.

## 8. Mandatory release gates

A release cannot be called global-production-ready until evidence exists for:

- Unit, integration, contract, and end-to-end tests.
- Authentication, authorization, tenant-isolation, and privilege-escalation tests.
- Load, soak, burst, and rate-limit tests at an agreed traffic profile.
- Dependency and container vulnerability scans.
- Backup restore, database failover, queue replay, and regional recovery drills.
- Observability, paging, incident runbooks, and cost alerts.
- Privacy, data-residency, retention, deletion, and processor reviews.
- Canary deployment, rollback, and release provenance.
- Live tests of each selected AI and external integration provider.

## 9. Decisions requiring Founder approval

The following are not selected or activated in this repository:

1. Cloud and hosting provider.
2. Primary and recovery regions and data-residency policy.
3. Identity provider and organization / tenant model.
4. Production database, queue, object store, and vector service.
5. AI providers, allowed models, budget ceilings, and data-sharing policy.
6. Monitoring, alerting, and incident-response ownership.
7. Production domain, DNS, certificates, and deployment window.
8. Any paid resource, public deployment, external integration, or production credential.

## 10. Current gap statement

The current branch provides a hardened local container foundation and a small authenticated API. It does **not** yet provide a globally scalable architecture in operation. The next engineering milestone is to replace local-only identity, persistence, and task execution with managed production services while preserving the approval and audit boundaries.
