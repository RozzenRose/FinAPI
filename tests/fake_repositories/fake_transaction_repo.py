from typing import List
from uuid import UUID

from app.domain.entities.transaction import Transaction
from app.domain.interfaces.transaction_repository import ITransactionRepository


class FakeTransactionRepo(ITransactionRepository):

    def __init__(self, transactions):
        self.transactions: List[Transaction] = transactions

    async def create_transaction(self, transaction: Transaction) -> None:
        self.transactions.append(transaction)
        return transaction

    async def get_all_transaction_by_account_id(self, account_id: UUID) -> List[Transaction]:
        result = []
        for txn in self.transactions:
            if any(entry.account_id == account_id for entry in txn.entries):
                result.append(txn)
        return sorted(result, key=lambda x: x.date, reverse=True)

    async def get_transaction_by_id(self, id: UUID) -> Transaction | None:
        for txn in self.transactions:
            if txn.id == id:
                return txn
        return None