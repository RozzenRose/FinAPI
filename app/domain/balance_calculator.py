from decimal import Decimal
from typing import List
from uuid import UUID

from app.domain.entities.account import Account
from app.domain.entities.transaction import Transaction, TransactionEntry
from app.domain.enums import EntryType, AccountType


class BalanceCalculator:

    def _normal_debit(self, account_id: UUID, transactions: List[Transaction]):
        balance = Decimal('0')

        for transaction in transactions:
            for entry in transaction.entries:
                if entry.account_id == account_id:
                    if entry.type == EntryType.DEBIT:
                        balance += entry.amount
                    else:
                        balance -= entry.amount

        return balance

    def _normal_credit(self, account_id: UUID, transactions: List[Transaction]):
        balance = Decimal('0')

        for transaction in transactions:
            for entry in transaction.entries:
                if entry.account_id == account_id:
                    if entry.type == EntryType.CREDIT:
                        balance += entry.amount
                    else:
                        balance -= entry.amount

        return balance

    def calculate(self,
                  account: Account,
                  transactions: list[Transaction]) -> Decimal:
        if account.type in (AccountType.ASSET, AccountType.EXPENSE):
            return self._normal_debit(account.id, transactions)
        if account.type in (AccountType.LIABILITY, AccountType.REVENUE):
            return self._normal_credit(account.id, transactions)