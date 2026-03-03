from dataclasses import dataclass

from app.domain.enums import AccountType, EntryType
from uuid import UUID
from decimal import Decimal
from datetime import datetime


@dataclass
class Account:
    id: UUID
    name: str
    type: AccountType

@dataclass
class TransactionEntry:
    account_id: UUID
    type: EntryType
    amount: Decimal

@dataclass
class Transaction:
    id: UUID
    transaction_id: UUID
    account_id: UUID
    description: str
    date: datetime
    entries: list[TransactionEntry]