from app.domain.entities.transaction import Transaction
from app.domain.interfaces.transaction_repository import ITransactionRepository
from app.infrastructure.bd.models.transaction import Transaction as TransactionModel
from app.infrastructure.bd.models.transaction_entry import TransactionEntry as TransactionEntryModel


class SqlAlchemyTransactionRepo(ITransactionRepository):

    def __init__(self, session):
        self.session = session


    async def create_transaction(self, transaction: Transaction) -> None:
        transaction_orm = TransactionModel(
            description=transaction.description,
            date=transaction.date,
        )

        transaction_orm.entries = [
            TransactionEntryModel(
                account_id=entry.account_id,
                type=entry.type.value,  # Enum → str
                amount=entry.amount,
            )
            for entry in transaction.entries
        ]

        self.session.add(transaction_orm)
        await self.session.commit()