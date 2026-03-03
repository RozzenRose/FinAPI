from typing import Annotated

from fastapi import APIRouter, Depends
from app.api.schemas.schemas_transaction import CreateTransactionRequest
from app.services.usecases.transaction_usecases import CreateTransactionUseCase
from app.infrastructure.di import get_create_transaction_usecase


router = APIRouter(prefix='/api', tags=['api'])


@router.post("/transactions")
async def create_transaction(request: CreateTransactionRequest,
                             use_case: Annotated[CreateTransactionUseCase, Depends(get_create_transaction_usecase)]):
    return await use_case.execute(description=request.description,
                                  date=request.date,
                                  raw_entries=request.entries)