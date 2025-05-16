from typing import List, Optional

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import models
from app.db.session import get_session
from app.schemas.partner import PartnerCreate, PartnerOut

router = APIRouter(prefix="/partners", tags=["Partners"])


@router.post("", response_model=PartnerOut)
async def create_partner(partner: PartnerCreate, db: AsyncSession = Depends(get_session)):
    obj = models.Partner(**partner.model_dump())
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj


@router.get("", response_model=List[PartnerOut])
async def list_partners(
    search: str | None = None, db: AsyncSession = Depends(get_session)
):
    stmt = select(models.Partner)
    if search:
        stmt = stmt.where(
            models.Partner.name.ilike(f"%{search}%")
            | models.Partner.identifier.ilike(f"%{search}%")
        )
    res = await db.execute(stmt)
    return res.scalars().all()
