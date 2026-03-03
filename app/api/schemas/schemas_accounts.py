from pydantic import BaseModel, field_validator, PositiveFloat
from app.domain.enums import AccountType


class CreateAccount(BaseModel):
    name: str
    type: AccountType
