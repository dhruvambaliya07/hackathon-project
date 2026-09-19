from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, String, func
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Interest(Base):
    __tablename__ = "interests"

    id: Mapped[UUID] = mapped_column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(120), nullable=False, unique=True, index=True)
    category: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    groups: Mapped[list["GroupInterest"]] = relationship(back_populates="interest", cascade="all, delete-orphan")
    events: Mapped[list["EventInterest"]] = relationship(back_populates="interest", cascade="all, delete-orphan")
    users: Mapped[list["UserInterest"]] = relationship(back_populates="interest", cascade="all, delete-orphan")