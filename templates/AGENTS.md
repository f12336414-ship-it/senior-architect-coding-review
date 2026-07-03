# Project agent guidance

## Business and ownership

- Business capabilities and owners:
- Authoritative data owners:
- Authentication/authorization boundaries:
- Risk approvers:

## Architecture

- Module/service boundaries:
- Accepted ADRs:
- Public API/event compatibility promises:
- Forbidden dependencies or shared writes:

## Commands

- Build:
- Unit tests:
- Integration tests:
- Type/lint/static analysis:
- Architecture/security checks:

## Change boundaries

- Allowed paths:
- Paths requiring explicit approval:
- Generated files:
- Production/deployment/database rules:

## Delivery

- Deployment sequence:
- Rollback/forward-fix:
- Required metrics and alerts:
- PR approval and evidence requirements:

Use `$senior-architect-coding-review` for architecture-sensitive work. Low-risk local changes should use its fast-path; review requests are read-only unless repair is explicitly requested.
