# Cloud Deployment Sketch (GCP) - ping5

## Finalized Strategy

Deploy ping5 on a single Google Compute Engine VM with persistent disk storage, running the existing Docker Compose stack.

This is the selected MVP approach because it is simple, low-friction, cost-aware, and aligns with the current application shape (single service with an always-on minute scheduler and SQLite).

## Why This Strategy Was Chosen

1. Operational simplicity
- One VM, one deploy path, one runtime model.
- No platform-level orchestration overhead.

2. Scheduler fit
- ping5 uses an in-process monitor loop aligned to minute boundaries.
- VM runtime guarantees continuous process execution without redesign.

3. Cost and ROI fit for MVP
- e2-micro/e2-small instance is sufficient for internal testing scale.
- Predictable baseline cost and straightforward capacity planning.

4. Persistence fit
- SQLite file stored on persistent disk.
- Data survives app and VM restarts.

## Proposed Topology

- 1x Compute Engine VM (single region)
- 1x Persistent Disk mounted on VM
- Docker + Docker Compose on VM
- ping5 stack launched via `docker compose up --build -d`

Data location:
- Container DB path: `/app/data/monitor.db`
- Persisted through Docker named volume and VM persistent disk.

## Deployment Plan (MVP)

1. Provision VM
- Machine: `e2-micro` to start (`e2-small` if needed)
- OS: Debian/Ubuntu LTS
- Region: nearest low-latency region

2. Prepare runtime
- Install Docker Engine + Compose plugin
- Create deployment directory, for example `/opt/ping5`

3. Deploy application
- Clone repository into `/opt/ping5`
- Run `docker compose up --build -d`

4. Access model
- Internal testing: restricted firewall source ranges or IAP/SSH tunnel
- No load balancer required for this MVP phase

5. Operate
- Use compose restart policy
- Optional: add a systemd unit to start compose on VM boot

## Options Evaluated and Omitted

1. GKE / GKE Autopilot
- Omitted now: overkill for single-service MVP, higher ops complexity than value.

2. Cloud Run / serverless first
- Omitted now: possible and sometimes cost-efficient, but less natural for an always-on in-process scheduler unless scheduler is redesigned.

3. App Engine first
- Omitted now: solid managed platform, but unnecessary abstraction for current internal MVP scope and deployment velocity goals.

4. Cloud Run + Cloud SQL (production-leaning path)
- Deferred: better suited once multi-instance scaling, stronger durability, and managed database operations are required.

## Risks and Explicit Trade-offs

- Single VM is not high availability.
- SQLite is not suitable for multi-instance writers.
- Security/compliance controls are intentionally minimal for internal MVP testing.

These trade-offs are accepted for this assignment phase.

## Near-Term Evolution Path (When Needed)

1. Move SQLite to Cloud SQL Postgres.
2. Split scheduler from API runtime if scaling requires independent control.
3. Migrate runtime to Cloud Run or GKE only when complexity is justified.
