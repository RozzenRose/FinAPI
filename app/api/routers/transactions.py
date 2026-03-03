from fastapi import APIRouter, Depends
from app.api.schemas.schemas_transaction import CreateTransactionRequest


router = APIRouter(prefix='/api', tags=['api'])


@router.post("/transactions")
async def create_transaction(request: CreateTransactionRequest):
    pass