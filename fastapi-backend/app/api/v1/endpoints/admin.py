from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func

from app.api import deps
from app.db.session import get_db
from app.models.user import User
from app.models.pricing_plan import PricingPlan
from app.schemas.user import User as UserSchema, UserUpdate
from app.schemas.pricing import PricingPlan as PricingPlanSchema, PricingPlanUpdate

router = APIRouter()

@router.get("/users", response_model=List[UserSchema])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(deps.get_admin_user)
) -> Any:
    result = await db.execute(select(User).offset(skip).limit(limit))
    users = result.scalars().all()
    return [UserSchema.model_validate(user) for user in users]

@router.get("/users/{user_id}", response_model=UserSchema)
async def get_user(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(deps.get_admin_user)
) -> Any:
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserSchema.model_validate(user)

@router.put("/users/{user_id}", response_model=UserSchema)
async def update_user(
    user_id: str,
    user_in: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(deps.get_admin_user)
) -> Any:
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    update_data = user_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)
        
    await db.commit()
    await db.refresh(user)
    return UserSchema.model_validate(user)

@router.delete("/users/{user_id}", response_model=dict)
async def deactivate_user(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(deps.get_admin_user)
) -> Any:
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    user.is_active = False
    await db.commit()
    return {"message": "User deactivated successfully"}

@router.get("/pricing", response_model=List[PricingPlanSchema])
async def get_pricing(
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(deps.get_admin_user)
) -> Any:
    result = await db.execute(select(PricingPlan))
    plans = result.scalars().all()
    return [PricingPlanSchema.model_validate(plan) for plan in plans]

@router.put("/pricing/{plan_id}", response_model=PricingPlanSchema)
async def update_pricing(
    plan_id: str,
    plan_in: PricingPlanUpdate,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(deps.get_admin_user)
) -> Any:
    result = await db.execute(select(PricingPlan).where(PricingPlan.id == plan_id))
    plan = result.scalars().first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
        
    update_data = plan_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(plan, field, value)
        
    await db.commit()
    await db.refresh(plan)
    return PricingPlanSchema.model_validate(plan)

@router.get("/stats", response_model=dict)
async def get_stats(
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(deps.get_admin_user)
) -> Any:
    # Total users
    result = await db.execute(select(func.count(User.id)))
    total_users = result.scalar_one()
    
    # Verified users
    result = await db.execute(select(func.count(User.id)).where(User.is_verified == True))
    verified_users = result.scalar_one()
    
    # Individual plan users
    result = await db.execute(select(func.count(User.id)).where(User.plan == "individual"))
    individual_users = result.scalar_one()
    
    # Team plan users
    result = await db.execute(select(func.count(User.id)).where(User.plan == "team"))
    team_users = result.scalar_one()
    
    return {
        "total_users": total_users,
        "verified_users": verified_users,
        "plans": {
            "individual": individual_users,
            "team": team_users,
            "none": total_users - individual_users - team_users
        }
    }
