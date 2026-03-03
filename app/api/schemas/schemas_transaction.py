from pydantic import BaseModel, Field, condecimal
from typing import List
from uuid import UUID
from datetime import datetime
from app.domain.enums import EntryType


class EntryItem(BaseModel):
    account_id: UUID = Field(..., alias="accountId")
    type: EntryType
    amount: condecimal(gt=0, decimal_places=2)  # >0, 2 знака после запятой


class CreateTransactionRequest(BaseModel):
    description: str
    date: datetime
    entries: List[EntryItem]

    # Дополнительно проверка бизнес-логики: сумма дебета == сумма кредита
    @property
    def total_debit(self) -> float:
        return sum(e.amount for e in self.entries if e.type == EntryType.DEBIT)

    @property
    def total_credit(self) -> float:
        return sum(e.amount for e in self.entries if e.type == EntryType.CREDIT)

    def validate_balance(self):
        if self.total_debit != self.total_credit:
            raise ValueError("Total debit must equal total credit")