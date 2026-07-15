import uuid
from datetime import datetime
from typing import Optional, List
import json

from sqlalchemy import String, Text, Boolean, Float, ForeignKey, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy import func

from app.db.base import Base, TimestampMixin

class SavedBusiness(Base, TimestampMixin):
    __tablename__ = "saved_businesses"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    business_name: Mapped[str] = mapped_column(String(255), nullable=False)
    website: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    country: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    facebook: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    instagram: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    lat: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    lon: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Audit fields
    audit_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    overall_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    seo_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    ssl_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    load_speed_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    responsiveness_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    social_links_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    image_alt_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    audit_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    audit_recommendations: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Relationship
    user = relationship("User", back_populates="saved_businesses")
