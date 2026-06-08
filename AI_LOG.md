# AI Collaboration Log (ping5)

## AI Tech Stack

- Editor assistant: GitHub Copilot
- Model used in this session: GPT-5.3-Codex

## Prompts That Shipped the Implementation

Representative prompt excerpts used to drive delivery:

1. Scope and architecture
- "Keep this strict MVP and lightweight."
- "Use FastAPI + SQLite with a minimal public API surface."

2. Frontend execution
- "Use plain HTML/CSS/JS instead of React for this assignment."
- "Implement auto-refresh and a manual check cycle trigger."

3. Monitoring behavior
- "Run automatic checks every minute, aligned to minute boundaries."
- "Manual refresh must run a fresh cycle before returning data."

4. Packaging and submission
- "Make it run with one docker compose up command."
- "Remove non-essential features and prepare clean submission docs."

## Course Corrections and Fixes

1. Over-engineering reduction
- Initial path considered heavier frontend choices.
- Final decision: static frontend for faster delivery and lower complexity.

2. TLS/certificate friction
- Local/corporate certificate chain issues affected outbound HTTPS and image builds.
- Fixes:
	- Runtime TLS toggle retained for monitor checks.
	- Docker build adjusted to work in constrained network trust environments.

3. Container persistence and ownership
- Container failed with `unable to open database file` due to volume mount ownership behavior.
- Fixes:
	- DB mount path moved to `/app/data`.
	- `MONITOR_DB_PATH` updated accordingly.
	- Fresh volume initialization validated.

4. UX behavior correction
- Manual refresh initially behaved as data reload only.
- Final behavior: manual action triggers immediate check cycle via `GET /api/v1/urls?refresh=true`.

## Final Outcomes

- MVP backend with persisted per-check history.
- Minimal dynamic frontend aligned with assignment requirements.
- One-command local containerized run path.
- Submission-ready README, AI log, and cloud deployment sketch.
