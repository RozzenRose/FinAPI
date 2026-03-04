from app.domain.entities.account import Account
from app.domain.interfaces.account_repository import IAccountRepository
from app.domain.exceptions import AccountAlreadyExists, AccountNotFound, WeHaveNotAnyAccounts, NoNameAccount
from app.domain.enums import AccountType

from uuid import UUID


class CreateAccountUseCase:

    def __init__(self, account_repo: IAccountRepository):
        self.account_repo = account_repo

    async def execute(self, name: str, type: AccountType) -> Account:
        if not name:
            raise NoNameAccount
        existing = await self.account_repo.get_by_name(name)
        if existing:
            raise AccountAlreadyExists(
                f"Account with name '{name}' already exists"
            )
        account = Account(name=name, type=type)
        await self.account_repo.save(account)
        return account


class GetAllAccountsUseCase:

    def __init__(self, account_repo: IAccountRepository):
        self.account_repo = account_repo

    async def execute(self) -> list[Account]:
        data = await self.account_repo.get_all()
        if not data:
            raise WeHaveNotAnyAccounts()
        return data


class GetAccountByIdUseCase:

    def __init__(self, account_repo: IAccountRepository):
        self.account_repo = account_repo

    async def execute(self, id: UUID):
        data = await self.account_repo.get_by_id(id)
        if not data:
            raise AccountNotFound(
                f"Account with {id} is not found"
            )
        return data
