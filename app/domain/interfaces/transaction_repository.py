from abc import ABC, abstractmethod
from uuid import UUID
from app.domain.entities.transaction import Transaction


class ITransactionRepository(ABC):

    @abstractmethod
    async def create_transaction(self, transaction: Transaction) -> None:
        pass

    @abstractmethod
    async def get_all_transaction(self) -> list[Transaction] | None:
        pass

    @abstractmethod
    async def get_transaction_by_id(self, id: UUID) -> Transaction | None:
        pass