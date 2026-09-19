from datetime import datetime
from uuid import UUID, uuid4

from pgvector.sqlalchemy import Vector
from sqlalchemy import CheckConstraint, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import EMBEDDING_DIMENSION, Base


class Group(Base):
    __tablename__ = "groups"
    __table_args__ = (CheckConstraint("member_count >= 0", name="ck_groups_member_count_nonnegative"),)

    id: Mapped[UUID] = mapped_column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(160), nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text)
    category: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    location: Mapped[str | None] = mapped_column(String(200), nullable=True)
    meeting_frequency: Mapped[str | None] = mapped_column(String(80), nullable=True)
    member_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    embedding: Mapped[list[float] | None] = mapped_column(Vector(EMBEDDING_DIMENSION), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    interests: Mapped[list["GroupInterest"]] = relationship(back_populates="group", cascade="all, delete-orphan")
    events: Mapped[list["Event"]] = relationship(back_populates="group", cascade="all, delete-orphan")


class GroupInterest(Base):
    __tablename__ = "group_interests"
    __table_args__ = (
        UniqueConstraint("group_id", "interest_id", name="uq_group_interests_group_interest"),
        CheckConstraint("weight >= 0 AND weight <= 1", name="ck_group_interests_weight_range"),
    )

    group_id: Mapped[UUID] = mapped_column(PostgresUUID(as_uuid=True), ForeignKey("groups.id", ondelete="CASCADE"), primary_key=True)
    interest_id: Mapped[UUID] = mapped_column(PostgresUUID(as_uuid=True), ForeignKey("interests.id", ondelete="CASCADE"), primary_key=True)
    weight: Mapped[float] = mapped_column(Float, nullable=False, default=1.0, server_default="1")

    group: Mapped["Group"] = relationship(back_populates="interests")
    interest: Mapped["Interest"] = relationship(back_populates="groups")