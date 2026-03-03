from sqlalchemy import select

from app.domain.interfaces.account_repository import IAccountRepository
from app.infrastructure.bd.models.account import Account as AccountModel
from app.domain.entities.account import Account


class SqlAlchemyAccountRepo(IAccountRepository):

    def __init__(self, session):
        self.session = session

    async def get_by_name(self, name: str) -> Account | None:
        result = await self.session.execute(
            select(AccountModel).where(AccountModel.name == name)
        )
        data = result.scalar_one_or_none()
        if not data:
            return None

        return Account(name=data.name, type=data.type)

    async def save(self, account: Account) -> None:
        model = AccountModel(
            name=account.name,
            type=account.type
        )
        self.session.add(model)
        await self.session.commit()

    async def get_all(self) -> list[Account]:
        result = await self.session.execute(select(AccountModel))
        data = result.scalars().all()

        return [Account(name=item.name, type=item.type) for item in data]