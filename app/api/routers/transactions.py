from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from app.api.schemas.schemas_transaction import CreateTransactionRequest
from app.services.usecases.transaction_usecases import (CreateTransactionUseCase, GetTransactionByIdUseCase,
                                                        GetTransactionByAccountsIdUseCase)
from app.infrastructure.di import (get_create_transaction_usecase, get_transaction_by_id_usecase,
                                   get_transactions_by_account_id_usecase)


router = APIRouter(prefix='/api', tags=['api'])


@router.post("/transactions")
async def create_transaction(request: CreateTransactionRequest,
                             use_case: Annotated[CreateTransactionUseCase, Depends(get_create_transaction_usecase)]):
    return await use_case.execute(description=request.description,
                                  date=request.date,
                                  raw_entries=request.entries)


@router.get("/transactions/{id}")
async def get_transaction_by_id(id: UUID,
                                use_case: Annotated[GetTransactionByIdUseCase, Depends(get_transaction_by_id_usecase)]):
    return await use_case.execute(id)


@router.get("/accounts/{id}/transactions")
async def get_transactions_by_account_id(id: UUID,
                                         use_case: Annotated[GetTransactionByAccountsIdUseCase,
                                         Depends(get_transactions_by_account_id_usecase)]):
    return await use_case.execute(id)