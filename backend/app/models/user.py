from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, DateTime, Float, ForeignKey, JSON, String, Text, func
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    email: Mapped[str] = mapped_column(String(320), nullable=False, unique=True, index=True)
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    goals: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list, server_default="[]")
    traits: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list, server_default="[]")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    interests: Mapped[list["UserInterest"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    recommendations: Mapped[list["Recommendation"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    feedback: Mapped[list["Feedback"]] = relationship(back_populates="user", cascade="all, delete-orphan")


class UserInterest(Base):
    __tablename__ = "user_interests"
    __table_args__ = (CheckConstraint("weight >= 0 AND weight <= 1", name="ck_user_interests_weight_range"),)

    user_id: Mapped[UUID] = mapped_column(PostgresUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    interest_id: Mapped[UUID] = mapped_column(PostgresUUID(as_uuid=True), ForeignKey("interests.id", ondelete="CASCADE"), primary_key=True)
    weight: Mapped[float] = mapped_column(Float, nullable=False, default=1.0, server_default="1")
    source: Mapped[str] = mapped_column(String(40), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    user: Mapped["User"] = relationship(back_populates="interests")
    interest: Mapped["Interest"] = relationship(back_populates="users")