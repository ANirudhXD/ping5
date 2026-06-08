from __future__ import annotations

import asyncio
import os
import time

import httpx

from app.repository import insert_health_checks, list_active_monitored_urls
from app.utils import current_ist_timestamp

CHECK_INTERVAL_SECONDS = int(os.getenv("CHECK_INTERVAL_SECONDS", "60"))
REQUEST_TIMEOUT_SECONDS = float(os.getenv("REQUEST_TIMEOUT_SECONDS", "5"))
MAX_CONCURRENCY = int(os.getenv("MAX_CONCURRENCY", "20"))
# Default false keeps local MVP behavior stable on corp-managed machines with custom TLS chains.
# Set REQUEST_VERIFY_TLS=true to enable strict certificate validation.
VERIFY_TLS = os.getenv("REQUEST_VERIFY_TLS", "false").strip().lower() not in {"0", "false", "no"}


async def _check_url(
    client: httpx.AsyncClient,
    semaphore: asyncio.Semaphore,
    monitored_url_id: int,
    url: str,
) -> dict[str, object]:
    async with semaphore:
        start = time.perf_counter()
        checked_at = current_ist_timestamp()

        try:
            response = await client.get(url, timeout=REQUEST_TIMEOUT_SECONDS, follow_redirects=True)
            elapsed_ms = int((time.perf_counter() - start) * 1000)
            is_up = 200 <= response.status_code < 400

            return {
                "monitored_url_id": monitored_url_id,
                "status": "up" if is_up else "down",
                "status_code": response.status_code,
                "response_time_ms": elapsed_ms,
                "error": None,
                "checked_at": checked_at,
            }
        except Exception as exc:  # noqa: BLE001
            elapsed_ms = int((time.perf_counter() - start) * 1000)
            return {
                "monitored_url_id": monitored_url_id,
                "status": "down",
                "status_code": None,
                "response_time_ms": elapsed_ms,
                "error": str(exc),
                "checked_at": checked_at,
            }


async def run_check_cycle() -> int:
    targets = list_active_monitored_urls()
    if not targets:
        return 0

    semaphore = asyncio.Semaphore(MAX_CONCURRENCY)
    async with httpx.AsyncClient(verify=VERIFY_TLS) as client:
        tasks = [
            _check_url(client, semaphore, target["id"], target["url"])
            for target in targets
        ]
        records = await asyncio.gather(*tasks)

    insert_health_checks(records)
    return len(records)


def _seconds_until_next_window(window_seconds: int) -> float:
    now = time.time()
    remainder = now % window_seconds
    wait_for = window_seconds - remainder
    if wait_for < 0.001:
        return float(window_seconds)
    return wait_for


async def monitor_loop(stop_event: asyncio.Event) -> None:
    while not stop_event.is_set():
        try:
            await asyncio.wait_for(
                stop_event.wait(), timeout=_seconds_until_next_window(CHECK_INTERVAL_SECONDS)
            )
            break
        except TimeoutError:
            pass

        try:
            await run_check_cycle()
        except Exception:  # noqa: BLE001
            # Scheduler loop should survive per-cycle failures and continue.
            pass
