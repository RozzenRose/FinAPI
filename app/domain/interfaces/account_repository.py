from abc import ABC, abstractmethod
from uuid import UUID
from app.domain.entities.account import Account


class IAccountRepository(ABC):

    @abstractmethod
    async def get_by_name(self, name: str) -> Account | None:
        pass

    @abstractmethod
    async def save(self, account: Account) -> None:
        pass

    @abstractmethod
    async def get_all(self) -> list[Account] | None:
        pass

    @abstractmethod
    async def get_by_id(self, id: UUID) -> Account | None:
        pass