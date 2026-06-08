from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.db import init_db
from app.monitor import monitor_loop, run_check_cycle
from app.repository import create_monitored_url, list_urls_with_latest_status
from app.schemas import URLCreateRequest, URLCreateResponse, URLDashboardItem
from app.utils import normalize_url

ROOT_DIR = Path(__file__).resolve().parents[2]
FRONTEND_DIR = ROOT_DIR / "frontend"


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    stop_event = asyncio.Event()
    monitor_task = asyncio.create_task(monitor_loop(stop_event))
    app.state.stop_event = stop_event
    app.state.monitor_task = monitor_task
    try:
        yield
    finally:
        stop_event.set()
        await monitor_task


app = FastAPI(
    title="ping5 API",
    description="ping5 MVP API for registering URLs and viewing latest uptime status.",
    version="0.1.0",
    lifespan=lifespan,
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


@app.get("/", include_in_schema=False)
def root_frontend() -> FileResponse:
    if not FRONTEND_DIR.exists() or not (FRONTEND_DIR / "index.html").exists():
        raise HTTPException(status_code=503, detail="Frontend assets are not available")
    return FileResponse(FRONTEND_DIR / "index.html")


@app.post("/api/v1/urls", response_model=URLCreateResponse, status_code=201)
def register_url(payload: URLCreateRequest) -> URLCreateResponse:
    try:
        normalized = normalize_url(payload.url)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    created = create_monitored_url(payload.url.strip(), normalized, payload.name)
    if created is None:
        raise HTTPException(status_code=409, detail="URL already registered")

    return URLCreateResponse(**created)


@app.get("/api/v1/urls", response_model=list[URLDashboardItem])
async def list_urls(refresh: bool = False) -> list[URLDashboardItem]:
    if refresh:
        await run_check_cycle()
    rows = list_urls_with_latest_status()
    return [URLDashboardItem(**row) for row in rows]
