# Provider-neutral review automation contract

## Inputs

- Repository and immutable commit SHA.
- PR/MR diff, issue/acceptance text and allowed paths.
- Project guidance and selected Skill version.
- Permission mode (`review-only` by default).
- Available build, test, static and architecture commands.

## Agent responsibilities

1. Determine quick/standard/high-risk depth.
2. Refuse formal design when G1 is not ready.
3. Run only authorized read/verification tools.
4. Emit `schemas/review-report.schema.json` JSON and a concise Markdown summary.
5. Never post approval, merge, deploy or mutate the branch from the review job.

## CI responsibilities

1. Validate JSON and archive raw response, commands and tool results.
2. Run `tools/evaluate_review_report.py`.
3. Map P0/P1 blocking findings to a failed required check.
4. Publish summary from a separate least-privilege job.
5. Require human approval for High/Critical and protected environments.

## Provider adapter

Each Codex, Claude Code, Cursor, Gemini CLI or other adapter must record provider, model/Agent version, prompt, Skill commit, permissions, tool list, duration and raw output. Do not compare providers without the same fixture, environment, number of runs and scoring policy.

## GitHub/GitLab presentation

Use one stable comment/check per run and update it rather than spamming comments. Include commit SHA, blocking IDs, advisory count, validation status and artifact link. Never let comment text itself determine merge status; use a required CI check.
