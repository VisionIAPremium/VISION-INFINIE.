# Airtable integration

## Selected workspace resource

The connected Airtable account exposed a base named **VISION INFINIE — AI Content OS**.
Its existing tables include Content Pipeline, Knowledge Sources, Video Production,
Publishing Calendar, Performance Intelligence, and Automation Registry.

The existing CareerOS bases are separate and must not be modified as part of this
integration.

## Current implementation

`core/integrations/airtable/client.py` provides a deliberately read-only REST
client. It supports bounded record reads and uses the official Airtable API.
It has no create, update, delete, automation, or publishing methods.

Configuration is read from environment variables at runtime:

- `AIRTABLE_BASE_ID`
- `AIRTABLE_TOKEN`

Never commit a token, paste it into source code, or include it in logs. Do not
store personal or sensitive records in this public repository. The token must
be created and managed by an authorized account holder, with only the minimum
read scopes required. Any real credential setup must comply with the service's
age and account requirements and appropriate adult supervision.

## Safe activation sequence

1. Review the Airtable base and confirm the exact tables and fields to expose.
2. Configure credentials outside the repository in an approved secret store.
3. Test read-only access against a non-sensitive test record.
4. Review data minimization, permissions, and logging before considering writes.
5. Require explicit Founder approval and a separate implementation review before
   adding any write or automation capability.

The linked Airtable account was inspected read-only. No Airtable records, tables,
fields, interfaces, or automations were changed by this integration work.
