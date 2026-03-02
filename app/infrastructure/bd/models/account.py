from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Enum

from app.infrastructure.bd.engine import Base
from app.domain.enums import AccountType

from typing import List
import uuid


class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
        index=True,
    )

    type: Mapped[AccountType] = mapped_column(
        Enum(AccountType, name="account_type"),
        nullable=False,
    )

    entries: Mapped[List["TransactionEntry"]] = relationship(
        back_populates="account",
        cascade="all, delete-orphan",
    )