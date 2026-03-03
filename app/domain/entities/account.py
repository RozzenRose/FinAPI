from dataclasses import dataclass
from app.domain.enums import AccountType
from uuid import UUID


@dataclass
class Account:
    id: UUID
    name: str
    type: AccountType