from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, DateTime, Float, ForeignKey, Integer, JSON, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import EMBEDDING_DIMENSION, Base


class Event(Base):
    __tablename__ = "events"
    __table_args__ = (
        CheckConstraint("capacity IS NULL OR capacity >= 0", name="ck_events_capacity_nonnegative"),
        CheckConstraint("end_time IS NULL OR end_time > start_time", name="ck_events_end_after_start"),
    )

    id: Mapped[UUID] = mapped_column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid4)
    group_id: Mapped[UUID] = mapped_column(PostgresUUID(as_uuid=True), ForeignKey("groups.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text)
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    end_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    location: Mapped[str] = mapped_column(String(200), nullable=False)
    capacity: Mapped[int | None] = mapped_column(Integer, nullable=True)
    image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    embedding: Mapped[list[float] | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    group: Mapped["Group"] = relationship(back_populates="events")
    interests: Mapped[list["EventInterest"]] = relationship(back_populates="event", cascade="all, delete-orphan")


class EventInterest(Base):
    __tablename__ = "event_interests"
    __table_args__ = (
        UniqueConstraint("event_id", "interest_id", name="uq_event_interests_event_interest"),
        CheckConstraint("weight >= 0 AND weight <= 1", name="ck_event_interests_weight_range"),
    )

    event_id: Mapped[UUID] = mapped_column(PostgresUUID(as_uuid=True), ForeignKey("events.id", ondelete="CASCADE"), primary_key=True)
    interest_id: Mapped[UUID] = mapped_column(PostgresUUID(as_uuid=True), ForeignKey("interests.id", ondelete="CASCADE"), primary_key=True)
    weight: Mapped[float] = mapped_column(Float, nullable=False, default=1.0, server_default="1")

    event: Mapped["Event"] = relationship(back_populates="interests")
    interest: Mapped["Interest"] = relationship(back_populates="events")