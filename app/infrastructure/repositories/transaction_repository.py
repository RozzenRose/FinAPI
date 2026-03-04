from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.domain.entities.transaction import Transaction, TransactionEntry
from app.domain.enums import EntryType
from app.domain.interfaces.transaction_repository import ITransactionRepository
from app.infrastructure.db.models.transaction import Transaction as TransactionModel
from app.infrastructure.db.models.transaction_entry import TransactionEntry as TransactionEntryModel


class SqlAlchemyTransactionRepo(ITransactionRepository):

    def __init__(self, session):
        self.session = session


    async def create_transaction(self, transaction: Transaction) -> None:
        transaction_orm = TransactionModel(
            id=transaction.id,
            description=transaction.description,
            timestamp=transaction.date,
        )
        transaction_orm.entries = [
            TransactionEntryModel(
                id=entry.id,
                account_id=entry.account_id,
                transaction_id=entry.account_id,
                type=entry.type.value,  # Enum → str
                amount=entry.amount,
            )
            for entry in transaction.entries
        ]
        self.session.add(transaction_orm)
        await self.session.commit()


    def _map_to_domain(self, data: TransactionModel) -> Transaction:
        return Transaction(
            id=data.id,
            description=data.description,
            date=data.timestamp,
            entries=[
                TransactionEntry(
                    id=entry.id,
                    account_id=entry.account_id,
                    transaction_id=entry.transaction_id,
                    type=EntryType(entry.type),
                    amount=entry.amount,
                ) for entry in data.entries
            ]
        )


    async def get_all_transaction_by_account_id(self, account_id: UUID) -> list[Transaction] | None:
        stmt = (
            select(TransactionModel)
            .join(TransactionModel.entries)  # JOIN entries
            .where(TransactionEntryModel.account_id == account_id)
            .options(selectinload(TransactionModel.entries))  # чтобы подтянуть все entries
            .order_by(TransactionModel.timestamp.desc())
            .distinct()
        )
        result = await self.session.execute(stmt)
        data = result.scalars().all()
        return [self._map_to_domain(item) for item in data]


    async def get_transaction_by_id(self, id: UUID) -> Transaction | None:
        stmt = (
            select(TransactionModel)
            .where(TransactionModel.id == id)
            .options(selectinload(TransactionModel.entries))
        )
        result = await self.session.execute(stmt)
        data = result.scalar_one_or_none()
        if data is None:
            return None
        return self._map_to_domain(data)