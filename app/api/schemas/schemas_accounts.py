from app.domain.enums import AccountType
from pydantic import BaseModel


class CreateAccount(BaseModel):
    name: str
    type: AccountType


