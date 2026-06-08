-- Starter schema for ping5 MVP

CREATE TABLE IF NOT EXISTS monitored_urls (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url TEXT NOT NULL,
    normalized_url TEXT NOT NULL UNIQUE,
    name TEXT,
    is_active INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%S+05:30', 'now', '+5 hours', '+30 minutes')),
    updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%S+05:30', 'now', '+5 hours', '+30 minutes'))
);

CREATE INDEX IF NOT EXISTS idx_monitored_urls_active
    ON monitored_urls (is_active);

CREATE TABLE IF NOT EXISTS health_checks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    monitored_url_id INTEGER NOT NULL REFERENCES monitored_urls(id) ON DELETE CASCADE,
    status TEXT NOT NULL CHECK (status IN ('up', 'down')),
    status_code INTEGER,
    response_time_ms INTEGER,
    error TEXT,
    checked_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%S+05:30', 'now', '+5 hours', '+30 minutes'))
);

CREATE INDEX IF NOT EXISTS idx_health_checks_url_checked_at
    ON health_checks (monitored_url_id, checked_at DESC);

CREATE INDEX IF NOT EXISTS idx_health_checks_checked_at
    ON health_checks (checked_at DESC);
