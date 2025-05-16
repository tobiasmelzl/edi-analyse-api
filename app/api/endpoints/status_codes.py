from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import models
from app.db.session import get_session
from app.schemas.status_code import StatusCodeOut

router = APIRouter(prefix="/status-codes", tags=["Status Codes"])


@router.get("", response_model=list[StatusCodeOut])
async def list_codes(db: AsyncSession = Depends(get_session)):
    res = await db.execute(select(models.StatusCode))
    return res.scalars().all()


@router.get("/{code}", response_model=StatusCodeOut)
async def get_code(code: int, db: AsyncSession = Depends(get_session)):
    obj = await db.get(models.StatusCode, code)
    if not obj:
        raise HTTPException(status_code=404, detail="Status‑Code not found")
    return obj
