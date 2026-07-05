import uuid
from typing import List

from sqlalchemy import String, Numeric, Boolean, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, JSONB

from app.db.base import Base, TimestampMixin


class PricingPlan(Base, TimestampMixin):
    __tablename__ = "pricing_plans"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    slug: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False, default=0.0)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    
    features: Mapped[list] = mapped_column(JSONB, default=list)
    
    is_popular: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    trial_days: Mapped[int] = mapped_column(default=0)

    def __repr__(self) -> str:
        return f"<PricingPlan {self.name}>"
