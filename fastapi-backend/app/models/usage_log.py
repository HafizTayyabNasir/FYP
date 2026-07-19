import uuid
from datetime import date
from sqlalchemy import Date, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base, TimestampMixin


class UsageLog(Base, TimestampMixin):
    __tablename__ = "usage_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    usage_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    emails_sent: Mapped[int] = mapped_column(Integer, default=0)
    ai_generations: Mapped[int] = mapped_column(Integer, default=0)
    
    # Relationships
    user = relationship("User")

    def __repr__(self) -> str:
        return f"<UsageLog {self.user_id} - {self.usage_date}>"
