from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, DateTime

from app.infrastructure.bd.engine import Base
from app.infrastructure.bd.models import TransactionEntry

from datetime import datetime
from typing import List
import uuid


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
    )

    description: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    entries: Mapped[List["TransactionEntry"]] = relationship(
        back_populates="transaction",
        cascade="all, delete-orphan",
    )