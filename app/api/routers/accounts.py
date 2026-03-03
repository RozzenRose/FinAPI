from http.client import HTTPException
from typing import Annotated

from fastapi import APIRouter, Depends
from app.api.schemas.schemas_accounts import CreateAccount
from app.domain.exceptions import AccountAlreadyExists
from app.infrastructure.di import get_create_account_use_case, get_all_acounts_usecase, get_account_by_name
from app.services.usecases.account_usecases import CreateAccountUseCase, GetAllAccounts, GetAccountByName

router = APIRouter(prefix='/api', tags=['api'])


@router.post("/accounts")
async def create_account_rout(account: CreateAccount,
                              use_case: Annotated[CreateAccountUseCase, Depends(get_create_account_use_case)]):
    return await use_case.execute(
        name=account.name,
        type=account.type
    )


@router.get("/accounts")
async def get_all_accounts(use_case: Annotated[GetAllAccounts, Depends(get_all_acounts_usecase)]):
    return await use_case.execute()


@router.get("/accounts/{name}")
async def get_account_by_name(name: str,
                              use_case: Annotated[GetAccountByName, Depends(get_account_by_name)]):
    return await use_case.execute(name)