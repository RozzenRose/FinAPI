from uuid import UUID

from app.domain.entities.account import Account
from app.domain.interfaces.account_repository import IAccountRepository


class FakeAccountRepo(IAccountRepository):

    def __init__(self, accounts):
        self.accounts: list[Account] = accounts

    async def get_by_name(self, name: str) -> Account | None:
        for account in self.accounts:
            if account.name == name:
                return account
        return None

    async def save(self, account: Account) -> None:
        self.accounts.append(account)

    async def get_all(self) -> list[Account]:
        return self.accounts

    async def get_by_id(self, id: UUID) -> Account | None:
        for account in self.accounts:
            if account.id == id:
                return account
        return None

