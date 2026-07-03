# Project guidance for Claude Code

Read the installed `senior-architect-coding-review` Skill for architecture-sensitive design, implementation, migration, and review.

## Project facts

- Business/domain owners:
- Module and data ownership:
- Public contracts:
- Build/test/static commands:
- Deployment and rollback:

## Permissions

- Default to read-only for review and diagnosis.
- Do not modify these paths without explicit approval:
- Do not add runtime dependencies or infrastructure without explicit approval.
- Do not run destructive git, filesystem, database, production, IAM, network, secret, or deployment operations without scoped approval and recovery evidence.

## Verification

- Required checks before handoff:
- High-risk approval roles:
- Critical specialist and risk-owner approval:

Keep this file project-specific. Do not copy the complete Skill into always-on context.
