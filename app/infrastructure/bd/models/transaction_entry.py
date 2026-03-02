from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import ForeignKey, Enum, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.bd.engine import Base
from app.domain.enums import EntryType

from decimal import Decimal
import uuid


class TransactionEntry(Base):
    __tablename__ = "transaction_entries"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    transaction_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("transactions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    account_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("accounts.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    type: Mapped[EntryType] = mapped_column(
        Enum(EntryType, name="entry_type"),
        nullable=False,
    )

    amount: Mapped[Decimal] = mapped_column(
        Numeric(18, 2),
        nullable=False,
    )

    transaction = relationship("Transaction", back_populates="entries")
    account = relationship("Account", back_populates="entries")