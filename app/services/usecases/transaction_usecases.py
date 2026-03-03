from datetime import datetime

from app.infrastructure.repositories.transaction_repository import SqlAlchemyTransactionRepo
from app.domain.entities.transaction import Transaction
from app.api.schemas.schemas_transaction import EntryItem
from app.domain.entities.transaction import TransactionEntry


class CreateTransactionUseCase:

    def __init__(self, transaction_repo: SqlAlchemyTransactionRepo):
        self.transaction_repo = transaction_repo

    async def execute(self, description: str, date: datetime, raw_entries: list[EntryItem]) -> Transaction:
        transaction = Transaction(description=description, timestamp=date)
        transaction_entries = [TransactionEntry(account_id=item.account_id,
                                                transaction_id=transaction.id,
                                                type=item.type,
                                                amount=item.amount)
                               for item in raw_entries]
        transaction.entries = transaction_entries
        await self.transaction_repo.create_transaction(transaction)
        return transaction