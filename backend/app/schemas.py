from __future__ import annotations

from pydantic import BaseModel


class URLCreateRequest(BaseModel):
    url: str
    name: str | None = None


class URLCreateResponse(BaseModel):
    id: int
    url: str
    name: str | None = None
    created_at: str


class LatestStatus(BaseModel):
    status: str
    status_code: int | None = None
    response_time_ms: int | None = None
    checked_at: str
    error: str | None = None


class URLDashboardItem(BaseModel):
    id: int
    url: str
    name: str | None = None
    created_at: str
    latest: LatestStatus | None = None
