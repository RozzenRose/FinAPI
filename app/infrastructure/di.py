from fastapi import Depends

from app.domain.balance_calculator import BalanceCalculator
from app.infrastructure.db.engine import session_factory
from app.services.usecases.account_usecases import CreateAccountUseCase, GetAllAccountsUseCase, GetAccountByIdUseCase
from app.infrastructure.repositories.account_repository import SqlAlchemyAccountRepo
from app.infrastructure.repositories.transaction_repository import SqlAlchemyTransactionRepo
from app.services.usecases.transaction_usecases import (CreateTransactionUseCase, GetTransactionByIdUseCase,
                                                        GetTransactionByAccountsIdUseCase)


async def get_db():
    async with session_factory() as session:
        yield session


def get_account_repo(
        session=Depends(get_db)
):
    return SqlAlchemyAccountRepo(session)


def get_create_account_usecase(
        repo=Depends(get_account_repo)
):
    return CreateAccountUseCase(repo)


def get_all_accounts_usecase(
        repo=Depends(get_account_repo)
):
    return GetAllAccountsUseCase(repo)


def get_account_by_id(
        repo=Depends(get_account_repo)
):
    return GetAccountByIdUseCase(repo)


def get_transaction_repo(
        session=Depends(get_db)
):
    return SqlAlchemyTransactionRepo(session)


def get_create_transaction_usecase(
        trans_repo=Depends(get_transaction_repo),
        accou_repo=Depends(get_account_repo)
):
    return CreateTransactionUseCase(trans_repo, accou_repo)


def get_transaction_by_id_usecase(
        repo = Depends(get_transaction_repo)
):
    return GetTransactionByIdUseCase(repo)


def get_balance_calculator() -> BalanceCalculator:
    return BalanceCalculator()


def get_transactions_by_account_id_usecase(
        trans_repo = Depends(get_transaction_repo),
        accou_repo=Depends(get_account_repo),
        balance_calculator=Depends(get_balance_calculator)
):
    return GetTransactionByAccountsIdUseCase(trans_repo, accou_repo, balance_calculator)
