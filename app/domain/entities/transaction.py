from dataclasses import dataclass, field
from datetime import datetime, timezone
from app.domain.enums import AccountType, EntryType
from uuid import UUID, uuid4
from decimal import Decimal
from datetime import datetime


@dataclass
class TransactionEntry:
    account_id: UUID
    transaction_id: UUID
    type: EntryType
    amount: Decimal
    id: UUID = field(default_factory=uuid4)


@dataclass
class Transaction:
    description: str
    timestamp: datetime
    entries: list[TransactionEntry] = field(default_factory=list)
    id: UUID = field(default_factory=uuid4)
