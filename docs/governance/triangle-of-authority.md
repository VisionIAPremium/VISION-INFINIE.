# VISION INFINIE — Triangle of Authority

**Status:** Governance rule adopted in the project documentation  
**Scope:** All project components, agents, tools, integrations, APIs, workflows, and data operations.

## 1. Authority structure

```text
                 FOUNDER
          Supreme authority / owner
          Vision, reserved approvals
                    |
                    v
                 DIRECTOR
        Central coordination and control
        Requests Founder approval when required
                    |
                    v
             AGENTS / MODULES
       Specialized, bounded execution units
        Request Director approval before action
```

### Level 1 — Founder

The Founder is the highest authority and owner of the project.

The Founder:
- defines and changes the strategic vision and governance rules;
- grants, limits, suspends, or revokes permissions;
- approves reserved decisions, sensitive-data access, external disclosure, and high-impact actions;
- may require review or stop any operation.

No Director or Agent may override a Founder decision.

### Level 2 — Director

The Director is the operational authority between the Founder and all Agents.

The Director:
- translates the Founder’s objectives into bounded missions;
- coordinates, supervises, and evaluates Agents;
- approves only actions within permissions delegated by the Founder;
- must request the Founder’s explicit approval for reserved decisions or access beyond delegated authority;
- records decisions and escalates uncertainty instead of assuming permission.

The Director cannot grant itself additional authority.

### Level 3 — Agents / Modules

VISION INFINIE may contain many specialized Agents or modules.

Each Agent:
- acts only within its assigned scope and granted permissions;
- requests approval from the Director before any action requiring approval;
- does not access unrelated data, expand its own permissions, change governance, or delegate authority unless explicitly allowed;
- stops when approval is denied, missing, expired, or ambiguous.

Agents report to the Director. They do not bypass the Director to obtain operational approval from the Founder.

## 2. Authorization chain

The default is **DENY**.

1. An Agent identifies the action, purpose, data, destination, and minimum permissions required.
2. The Agent requests authorization from the Director.
3. If the action is within the Director's delegated authority, the Director may approve or deny it.
4. If the action is reserved to the Founder or exceeds the Director's delegation, the Director must request the Founder's explicit approval.
5. The action proceeds only after the required approval is recorded.
6. Approval is limited to the stated purpose, data, operation, duration, and recipient. It is not a general or permanent permission.

A request, silence, previous approval for another task, or technical capability is **not** authorization.

## 3. Protected data and external services

- Sensitive personal data, credentials, private documents, and confidential information must not be placed in the source repository.
- No Agent, model provider, API, automation, or external integration may receive protected data without an explicit, scoped authorization through the chain above.
- Use the minimum data necessary; redact or pseudonymize wherever practical.
- Secrets must be stored in an approved secret manager or protected runtime environment, never in source code, commits, logs, issues, or chat.
- Data access and approvals should be auditable. Logs must not copy the sensitive data they are meant to protect.
- If the permission boundary cannot be enforced or verified, the operation must stop.

## 4. GitHub and CI boundary

GitHub is a hosting and execution platform, not an authority in the project hierarchy. Repository permissions and workflow permissions must be kept to the minimum required.

The current Python test workflow declares:

```yaml
permissions:
  contents: read
```

This grants the workflow read access to repository contents for its job; it does not establish a universal privacy boundary. Do not place protected personal data or secrets in the repository. Review any future workflow permission increase before merging it.

**Important platform limitation:** GitHub operates the hosting service and processes repository contents according to its service and account settings. A policy file in this repository cannot prevent the hosting provider itself from processing data stored there. The practical protection is to keep sensitive data out of the repository and carefully control connected services, tokens, secrets, and workflow permissions.

## 5. Enforcement and change control

- New integrations and Agents start with no access to protected data and no external-action permissions.
- Every permission grant must identify the approver, scope, purpose, duration, and revocation method.
- Denials and revocations must be respected immediately.
- Governance changes require explicit Founder approval.
- Where implementation does not yet technically enforce a rule, the limitation must be documented; documentation alone must not be represented as a security control.

## 6. Non-negotiable principle

**The Founder authorizes. The Director governs. The Agents execute within delegated limits.**

No lower level may claim, assume, or create the authority of a higher level.


## 7. Single communication gateway

The Founder communicates with the Director only. The Director is the single management gateway between the Founder and the Agent workforce.

- Agents may send operational requests, status, and results to the Director.
- The Director assigns work to Agents and receives their reports.
- Agents must not address, message, notify, or request operational approval directly from the Founder.
- The Director handles routine work within delegated authority and escalates reserved decisions to the Founder.
- The Director is responsible for consolidating Agent outputs before reporting to the Founder.
- An Agent that cannot proceed must stop and report the blocker to the Director; it must not bypass the chain.

The application-level routing policy is implemented in `core/governance/authority.py`. The policy tests are in `tests/test_authority.py`.

**Enforcement limitation:** the current module evaluates declared roles and approval flags; it does not authenticate identities, provide a messaging gateway, or intercept every external integration. Until those controls are connected to trusted authentication and all communication adapters, this is an application policy check—not a complete security boundary.
