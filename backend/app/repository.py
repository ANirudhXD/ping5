from __future__ import annotations

import sqlite3
from typing import Any

from app.db import get_connection
from app.utils import current_ist_timestamp


def create_monitored_url(url: str, normalized_url: str, name: str | None) -> dict[str, Any] | None:
    query = """
    INSERT INTO monitored_urls (url, normalized_url, name, created_at, updated_at)
    VALUES (?, ?, ?, ?, ?)
    """

    timestamp = current_ist_timestamp()

    with get_connection() as connection:
        try:
            cursor = connection.execute(query, (url, normalized_url, name, timestamp, timestamp))
            connection.commit()
        except sqlite3.IntegrityError as exc:
            if "UNIQUE constraint failed" in str(exc):
                return None
            raise

        row = connection.execute(
            "SELECT id, url, name, created_at FROM monitored_urls WHERE id = ?",
            (cursor.lastrowid,),
        ).fetchone()

    return dict(row) if row else None


def list_active_monitored_urls() -> list[dict[str, Any]]:
    query = """
    SELECT id, url
    FROM monitored_urls
    WHERE is_active = 1
    ORDER BY id
    """

    with get_connection() as connection:
        rows = connection.execute(query).fetchall()

    return [dict(row) for row in rows]


def insert_health_checks(records: list[dict[str, Any]]) -> None:
    if not records:
        return

    query = """
    INSERT INTO health_checks (
        monitored_url_id,
        status,
        status_code,
        response_time_ms,
        error,
        checked_at
    ) VALUES (?, ?, ?, ?, ?, ?)
    """

    params = [
        (
            record["monitored_url_id"],
            record["status"],
            record["status_code"],
            record["response_time_ms"],
            record["error"],
            record["checked_at"],
        )
        for record in records
    ]

    with get_connection() as connection:
        connection.executemany(query, params)
        connection.commit()


def list_urls_with_latest_status() -> list[dict[str, Any]]:
    query = """
    SELECT
        mu.id,
        mu.url,
        mu.name,
        mu.created_at,
        hc.status,
        hc.status_code,
        hc.response_time_ms,
        hc.checked_at,
        hc.error
    FROM monitored_urls mu
    LEFT JOIN health_checks hc
        ON hc.id = (
            SELECT hc2.id
            FROM health_checks hc2
            WHERE hc2.monitored_url_id = mu.id
            ORDER BY hc2.checked_at DESC, hc2.id DESC
            LIMIT 1
        )
    ORDER BY mu.id
    """

    with get_connection() as connection:
        rows = connection.execute(query).fetchall()

    result: list[dict[str, Any]] = []
    for row in rows:
        item = {
            "id": row["id"],
            "url": row["url"],
            "name": row["name"],
            "created_at": row["created_at"],
            "latest": None,
        }

        if row["checked_at"] is not None:
            item["latest"] = {
                "status": row["status"],
                "status_code": row["status_code"],
                "response_time_ms": row["response_time_ms"],
                "checked_at": row["checked_at"],
                "error": row["error"],
            }

        result.append(item)

    return result
