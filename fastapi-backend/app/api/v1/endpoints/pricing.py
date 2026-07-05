from typing import Any, List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.session import get_db
from app.models.pricing_plan import PricingPlan
from app.schemas.pricing import PricingPlan as PricingPlanSchema

router = APIRouter()

@router.get("/plans", response_model=List[PricingPlanSchema])
async def get_plans(
    db: AsyncSession = Depends(get_db)
) -> Any:
    result = await db.execute(select(PricingPlan).where(PricingPlan.is_active == True))
    plans = result.scalars().all()
    return [PricingPlanSchema.model_validate(plan) for plan in plans]
