from fastapi import Depends

from app.infrastructure.bd.engine import session_factory
from app.services.usecases.account_usecases import CreateAccountUseCase, GetAllAccountsUseCase, GetAccountByIdUseCase
from app.infrastructure.repositories.account_repository import SqlAlchemyAccountRepo


async def get_db():
    async with session_factory() as session:
        yield session


def get_account_repo(
        session=Depends(get_db)
):
    return SqlAlchemyAccountRepo(session)


def get_create_account_use_case(
        repo=Depends(get_account_repo)
):
    return CreateAccountUseCase(repo)


def get_all_acounts_usecase(
        repo=Depends(get_account_repo)
):
    return GetAllAccountsUseCase(repo)


def get_account_by_name(
        repo=Depends(get_account_repo)
):
    return GetAccountByIdUseCase(repo)