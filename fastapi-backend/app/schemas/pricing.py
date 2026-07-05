from pydantic import BaseModel
from typing import List, Optional
import uuid

class PricingPlanBase(BaseModel):
    slug: str
    name: str
    price: float
    description: Optional[str] = None
    features: List[str] = []
    is_popular: bool = False
    is_active: bool = True
    trial_days: int = 0

class PricingPlanCreate(PricingPlanBase):
    pass

class PricingPlanUpdate(PricingPlanBase):
    slug: Optional[str] = None
    name: Optional[str] = None
    price: Optional[float] = None

class PricingPlan(PricingPlanBase):
    id: uuid.UUID

    class Config:
        from_attributes = True
