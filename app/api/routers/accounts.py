from http.client import HTTPException
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from app.api.schemas.schemas_accounts import CreateAccount
from app.domain.exceptions import AccountAlreadyExists
from app.infrastructure.di import get_create_account_use_case, get_all_acounts_usecase, get_account_by_id
from app.services.usecases.account_usecases import (CreateAccountUseCase,
                                                    GetAllAccountsUseCase,
                                                    GetAccountByIdUseCase)

router = APIRouter(prefix='/api', tags=['api'])


@router.post("/accounts")
async def create_account_rout(account: CreateAccount,
                              use_case: Annotated[CreateAccountUseCase, Depends(get_create_account_use_case)]):
    return await use_case.execute(
        name=account.name,
        type=account.type
    )


@router.get("/accounts")
async def get_all_accounts(use_case: Annotated[GetAllAccountsUseCase, Depends(get_all_acounts_usecase)]):
    return await use_case.execute()


@router.get("/accounts/{id}")
async def get_account_by_name(id: UUID,
                              use_case: Annotated[GetAccountByIdUseCase, Depends(get_account_by_id)]):
    return await use_case.execute(id)