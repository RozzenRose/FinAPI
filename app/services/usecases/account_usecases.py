from app.domain.entities.account import Account
from app.domain.interfaces.account_repository import IAccountRepository
from app.domain.exceptions import AccountAlreadyExists, AccountNotFound, WeHaveNotAnyAccounts
from app.domain.enums import AccountType


class CreateAccountUseCase:

    def __init__(self, account_repo: IAccountRepository):
        self.account_repo = account_repo

    async def execute(self, name: str, type: AccountType) -> Account:
        # Проверка бизнес-инварианта
        existing = await self.account_repo.get_by_name(name)
        if existing:
            raise AccountAlreadyExists(
                f"Account with name '{name}' already exists"
            )

        # Создание сущности
        account = Account(name=name, type=type)

        # Сохранение
        await self.account_repo.save(account)

        return account


class GetAllAccounts:

    def __init__(self, account_repo: IAccountRepository):
        self.account_repo = account_repo

    async def execute(self) -> list[Account]:
        data = await self.account_repo.get_all()
        if not data:
            raise WeHaveNotAnyAccounts()
        return data


class GetAccountByName:

    def __init__(self, account_repo: IAccountRepository):
        self.account_repo = account_repo

    async def execute(self, name: str) -> Account:
        data = await self.account_repo.get_by_name(name)
        if not data:
            raise AccountNotFound(
                f"Account {name} is not found"
            )
        return data
