from __future__ import annotations

from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import models
from app.db.session import get_session
from app.schemas.kpi import KPI, KPIEntry

router = APIRouter(prefix="/kpi", tags=["KPIs"])


# Hilfsfunktionen

def _default_dates(
    start: Optional[datetime], end: Optional[datetime]
) -> tuple[datetime, datetime]:
    if not start:
        start = datetime.utcnow() - timedelta(days=30)
    if not end:
        end = datetime.utcnow()
    return start, end


def _partner_filter(
    stmt,
    partner_id: int | None,
    partner_name: str | None,
    partner_identifier: str | None,
):
    """
    Ergänzt das Statement um einen Partner-Filter
    – je nachdem, welcher Parameter gesetzt ist.
    """
    # nur einen Filter zulassen
    if sum(bool(x) for x in (partner_id, partner_name, partner_identifier)) > 1:
        raise HTTPException(
            status_code=400,
            detail="Nur einer der Parameter partner_id, partner_name oder partner_identifier darf gesetzt sein.",
        )

    # nach ID filtern
    if partner_id:
        return stmt.where(models.Transaction.partner_id == partner_id)

    # nach Name oder Identifier filtern
    if partner_name or partner_identifier:
        subq = select(models.Partner.id)
        if partner_name:
            subq = subq.where(models.Partner.name.ilike(f"%{partner_name}%"))
        else:
            subq = subq.where(models.Partner.identifier == partner_identifier)
        return stmt.where(models.Transaction.partner_id.in_(subq))

    # kein Filter
    return stmt


# KPI nach Partner (IN/OUT/ERROR)

@router.get("/partner", response_model=List[KPI])
async def kpi_partner(
    partner_id: int | None = None,
    partner_name: str | None = None,
    partner_identifier: str | None = None,
    start_date: datetime | None = Query(None, alias="from"),
    end_date: datetime | None = Query(None, alias="to"),
    db: AsyncSession = Depends(get_session),
):
    start_date, end_date = _default_dates(start_date, end_date)
    t = models.Transaction

    stmt = (
        select(
            t.partner_id,
            func.sum(case((t.direction == "INBOUND", 1), else_=0)).label("inbound"),
            func.sum(case((t.direction == "OUTBOUND", 1), else_=0)).label("outbound"),
            func.sum(case((t.status != 40, 1), else_=0)).label("errors"),
        )
        .where(t.created_at.between(start_date, end_date))
        .group_by(t.partner_id)
    )
    stmt = _partner_filter(stmt, partner_id, partner_name, partner_identifier)

    rows = (await db.execute(stmt)).all()
    return [
        KPI(
            data=[
                KPIEntry(category="INBOUND", count=r.inbound),
                KPIEntry(category="OUTBOUND", count=r.outbound),
                KPIEntry(category="ERRORS", count=r.errors),
            ],
            period_start=start_date,
            period_end=end_date,
        )
        for r in rows
    ]


# KPI: Nachrichtenzahl INBOUND/OUTBOUND

@router.get("/message-count", response_model=KPI)
async def kpi_message_count(
    partner_id: int | None = None,
    partner_name: str | None = None,
    partner_identifier: str | None = None,
    start_date: datetime | None = Query(None, alias="from"),
    end_date: datetime | None = Query(None, alias="to"),
    db: AsyncSession = Depends(get_session),
):
    start_date, end_date = _default_dates(start_date, end_date)
    t = models.Transaction

    stmt = (
        select(t.direction, func.count().label("count"))
        .where(t.created_at.between(start_date, end_date))
        .group_by(t.direction)
    )
    stmt = _partner_filter(stmt, partner_id, partner_name, partner_identifier)

    rows = (await db.execute(stmt)).all()
    data = [KPIEntry(category=d, count=c) for d, c in rows]
    return KPI(data=data, period_start=start_date, period_end=end_date)


# KPI: Nachrichten pro Nachrichtentyp

@router.get("/message-type", response_model=KPI)
async def kpi_message_type(
    partner_id: int | None = None,
    partner_name: str | None = None,
    partner_identifier: str | None = None,
    start_date: datetime | None = Query(None, alias="from"),
    end_date: datetime | None = Query(None, alias="to"),
    db: AsyncSession = Depends(get_session),
):
    start_date, end_date = _default_dates(start_date, end_date)
    t = models.Transaction

    stmt = (
        select(t.message_type, func.count().label("count"))
        .where(t.created_at.between(start_date, end_date))
        .group_by(t.message_type)
    )
    stmt = _partner_filter(stmt, partner_id, partner_name, partner_identifier)

    rows = (await db.execute(stmt)).all()
    data = [KPIEntry(category=typ, count=c) for typ, c in rows]
    return KPI(data=data, period_start=start_date, period_end=end_date)


# KPI: Fehlerrate %

@router.get("/error-rate", response_model=KPI)
async def kpi_error_rate(
    partner_id: int | None = None,
    partner_name: str | None = None,
    partner_identifier: str | None = None,
    start_date: datetime | None = Query(None, alias="from"),
    end_date: datetime | None = Query(None, alias="to"),
    db: AsyncSession = Depends(get_session),
):
    start_date, end_date = _default_dates(start_date, end_date)
    t = models.Transaction

    total_stmt = select(func.count()).where(t.created_at.between(start_date, end_date))
    err_stmt = select(func.count()).where(
        t.created_at.between(start_date, end_date), t.status != 40
    )

    total_stmt = _partner_filter(total_stmt, partner_id, partner_name, partner_identifier)
    err_stmt = _partner_filter(err_stmt, partner_id, partner_name, partner_identifier)

    total = (await db.scalar(total_stmt)) or 0
    errors = (await db.scalar(err_stmt)) or 0
    rate = round((errors / total) * 100, 2) if total else 0

    return KPI(
        data=[KPIEntry(category="ERROR_RATE_%", count=rate)],
        period_start=start_date,
        period_end=end_date,
    )
