from dataclasses import dataclass, field
from app.domain.enums import EntryType
from uuid import UUID, uuid4
from decimal import Decimal
from datetime import datetime
from app.domain.exceptions import (EntriesQuantityIsWrong,
                                   NoCreditEntries,
                                   NoDebitEntries,
                                   SumOfDebitIsNotPositive,
                                   SumOfCreditIsNotPositive,
                                   DebitIsNotEqualCredit)


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

    def validate(self):
        if len(self.entries) < 2:
            raise EntriesQuantityIsWrong(f"The number of entries must be two or more. Received: {len(self.entries)}")

        debit_total = Decimal('0')
        credit_total = Decimal('0')
        debit_exists = False
        credit_exists = False

        for entry in self.entries:
            if entry.type == EntryType.DEBIT:
                debit_exists = True
                debit_total += entry.amount
            elif entry.type == EntryType.CREDIT:
                credit_exists = True
                credit_total += entry.amount

        if not debit_exists:
            raise NoDebitEntries()

        if not credit_exists:
            raise NoCreditEntries()

        if debit_total < 0:
            raise SumOfDebitIsNotPositive

        if credit_total < 0:
            raise SumOfCreditIsNotPositive

        if debit_total != credit_total:
            raise DebitIsNotEqualCredit()