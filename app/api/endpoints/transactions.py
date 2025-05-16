from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_session
from app.db import models
from app.schemas.transaction import TransactionOut

router = APIRouter(prefix="/transactions", tags=["Transactions"])

@router.get("", response_model=List[TransactionOut])
async def list_transactions(
    partner_id: Optional[int] = None,
    message_type: Optional[str] = None,
    direction: Optional[str] = None,
    status: Optional[int] = None,
    start_date: Optional[datetime] = Query(None, alias="from"),
    end_date: Optional[datetime] = Query(None, alias="to"),
    db: AsyncSession = Depends(get_session),
):
    stmt = select(models.Transaction)
    filters = []
    if partner_id:
        filters.append(models.Transaction.partner_id == partner_id)
    if message_type:
        filters.append(models.Transaction.message_type == message_type)
    if direction:
        filters.append(models.Transaction.direction == direction)
    if status is not None:
        filters.append(models.Transaction.status == status)
    if start_date:
        filters.append(models.Transaction.created_at >= start_date)
    if end_date:
        filters.append(models.Transaction.created_at <= end_date)
    if filters:
        stmt = stmt.where(and_(*filters))
    res = await db.execute(stmt)
    return res.scalars().all()

@router.get("/errors", response_model=List[TransactionOut])
async def list_errors(db: AsyncSession = Depends(get_session)):
    res = await db.execute(select(models.Transaction).where(models.Transaction.status != 40))
    return res.scalars().all()
