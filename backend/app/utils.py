from __future__ import annotations

from datetime import datetime, timedelta, timezone
from urllib.parse import urlsplit, urlunsplit

IST = timezone(timedelta(hours=5, minutes=30))


def current_ist_timestamp() -> str:
    return datetime.now(IST).isoformat(timespec="seconds")


def normalize_url(raw_url: str) -> str:
    value = raw_url.strip()
    split = urlsplit(value)

    if split.scheme.lower() not in {"http", "https"}:
        raise ValueError("URL must start with http:// or https://")

    if not split.hostname:
        raise ValueError("URL must include a valid host")

    scheme = split.scheme.lower()
    hostname = split.hostname.lower()
    netloc = f"{hostname}:{split.port}" if split.port else hostname

    path = split.path or ""
    if path == "/":
        path = ""

    return urlunsplit((scheme, netloc, path, split.query, ""))
