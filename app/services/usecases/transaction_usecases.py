from datetime import datetime

from app.infrastructure.repositories.transaction_repository import SqlAlchemyTransactionRepo
from app.infrastructure.repositories.account_repository import SqlAlchemyAccountRepo
from app.domain.entities.transaction import Transaction
from app.api.schemas.schemas_transaction import EntryItem
from app.domain.entities.transaction import TransactionEntry
from app.domain.exceptions import AccountNotFound


class CreateTransactionUseCase:

    def __init__(self,
                 transaction_repo: SqlAlchemyTransactionRepo,
                 account_repo: SqlAlchemyAccountRepo):
        self.transaction_repo = transaction_repo
        self.account_repo = account_repo

    async def execute(self, description: str, date: datetime, raw_entries: list[EntryItem]) -> Transaction:
        # Build objects
        transaction = Transaction(description=description, timestamp=date)
        transaction_entries = [TransactionEntry(account_id=item.account_id,
                                                transaction_id=transaction.id,
                                                type=item.type,
                                                amount=item.amount)
                               for item in raw_entries]
        transaction.entries = transaction_entries
        # Check business rules
        transaction.validate()
        # Check account existing
        for item in transaction.entries:
            if not await self.account_repo.get_by_id(item.account_id):
                raise AccountNotFound(f"Account ({item.account_id}) not found")
        # Save transaction data
        await self.transaction_repo.create_transaction(transaction)
        return transaction