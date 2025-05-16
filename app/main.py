from __future__ import annotations

import asyncio
from datetime import datetime
from fastapi import APIRouter, Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from app.api import deps
from app.api import auth
from app.api.endpoints import (
    health,
    partners,
    transactions,
    kpis,
    status_codes,
)
from app.core.config import settings
from app.db import models
from app.db.session import engine

# FastAPI‑App

app = FastAPI(title="EDI_Analyse_API", version="0.1.0")

# Logging (Loguru)

logger.add("logs/api.log", rotation="10 MB", retention="14 days", compression="zip")

# optionaler Root-Endpoint
@app.get("/")
def root():
    return {"msg": "EDI Analyse-API – siehe http://127.0.0.1:8000/docs ---> © Tobias Melzl"}


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = datetime.utcnow()
    response = await call_next(request)
    dur = (datetime.utcnow() - start).total_seconds() * 1_000
    logger.info(f"{request.method} {request.url.path} → {response.status_code} ({dur:.1f} ms)")
    return response

# Datenbank – Tabellen anlegen (Dev) & Demo‑User seeden

async def _bootstrap() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)

    async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with async_session() as session:
        demo_exists = await session.scalar(select(models.User).where(models.User.username == "demo"))
        if not demo_exists:
            from app.api.auth import get_password_hash

            session.add(models.User(username="demo", hashed_password=get_password_hash("demo")))
            await session.commit()
            
@app.on_event("startup")
async def init_db():
    await _bootstrap()

#asyncio.get_event_loop().run_until_complete(_bootstrap())

# Globaler API‑Router  (/api …)
api_router = APIRouter(prefix="/api")

# Öffentliche Route
api_router.include_router(health.router)

# Geschützte Routen (API‑Key oder JWT notwendig)
secured_routers = [
    partners.router,
    transactions.router,
    kpis.router,
    status_codes.router,
    auth.router,
]
for r in secured_routers:
    api_router.include_router(r, dependencies=[Depends(deps.verify_api_key)])

app.include_router(api_router)


# CORS (alle – internes Netz)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
