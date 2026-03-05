from pydantic import BaseModel, Field, condecimal
from typing import List
from uuid import UUID
from datetime import datetime
from app.domain.enums import EntryType


class EntryItem(BaseModel):
    account_id: UUID = Field(..., alias="accountId")
    type: EntryType
    amount: condecimal(decimal_places=2)  # >0, 2 знака после запятой


class CreateTransactionRequest(BaseModel):
    description: str
    date: datetime
    entries: List[EntryItem]