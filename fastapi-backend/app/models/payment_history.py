import uuid
from decimal import Decimal
from sqlalchemy import String, Numeric, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base, TimestampMixin


class PaymentHistory(Base, TimestampMixin):
    __tablename__ = "payment_history"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(10), default="USD")
    plan_name: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="completed") # 'completed', 'failed', 'refunded'
    transaction_id: Mapped[str] = mapped_column(String(100), nullable=True)
    
    # Relationships
    user = relationship("User")

    def __repr__(self) -> str:
        return f"<PaymentHistory {self.amount} {self.currency} for {self.plan_name}>"
