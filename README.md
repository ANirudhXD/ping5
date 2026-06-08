# ping5

Lightweight uptime monitor MVP with a FastAPI backend, static frontend dashboard, minute-aligned health checks, and Docker Compose one-command startup.

## Assignment Snapshot

- Backend API: register URLs, run periodic checks, store per-check metrics.
- Frontend UI: show current status and latest response time dynamically.
- Containerization: one-command local spin-up with Docker Compose.
- Deployment sketch: GCP strategy documented in CLOUD_SKETCH.md.

## 1-Line Setup

From the repository root:

```bash
docker compose up --build -d
```

Open:
- Dashboard: http://127.0.0.1:8000/

Stop:

```bash
docker compose down
```

Stop and remove DB volume (destructive):

```bash
docker compose down -v
```

## Repository Structure

- `backend/` API, scheduler, DB schema, and persistence logic.
- `frontend/` static HTML/CSS/JS status dashboard.
- `docs/` build journal, strategy notes, and helper runbook.
- `docker-compose.yml` local orchestration.
- `Dockerfile` backend runtime image.

## What the App Does

1. Register monitor targets with `POST /api/v1/urls`.
2. Run health checks at whole-minute boundaries.
3. Store each individual check in SQLite (`status_code`, `response_time_ms`, `checked_at`, `status`, `error`).
4. Return latest status snapshots with `GET /api/v1/urls`.
5. Display real-time status on the dashboard with 60-second auto refresh and manual check cycle trigger.

## API Endpoints

- `POST /api/v1/urls`
- `GET /api/v1/urls`
- `GET /api/v1/urls?refresh=true` (manual immediate check cycle, then latest data)

## Testing Steps (Required Verification)

1. Start the app with `docker compose up --build -d`.
2. Open the dashboard at `http://127.0.0.1:8000/`.
3. Add a healthy URL, for example `https://example.com`.
4. Add an intentionally broken URL, for example `http://nonexistent.invalid`.
5. Click `Manual Check Cycle`.
6. Confirm the healthy URL shows `UP` and the broken URL shows `DOWN`.
7. Wait for the next minute boundary and confirm automatic refresh updates the status board.

## Data Persistence

- Docker volume name: `ping5_ping5_data`
- Container DB path: `/app/data/monitor.db`
- Compose env: `MONITOR_DB_PATH=/app/data/monitor.db`

Because SQLite is stored in a named volume, data persists across `docker compose down`. Data is only removed with `docker compose down -v`.

## Cloud Deployment Sketch (GCP)

Finalized MVP recommendation:

1. Single Compute Engine VM.
2. Persistent disk-backed SQLite data.
3. Existing Docker Compose runtime for deployment parity.

Rationale and omitted-option analysis are documented in CLOUD_SKETCH.md.

## AI Collaboration Log (Summary)

See `AI_LOG.md` for the explicit tooling, prompts, corrections, and final decisions used to build this submission.
