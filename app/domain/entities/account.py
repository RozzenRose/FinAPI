from dataclasses import dataclass
from app.domain.enums import AccountType


@dataclass
class Account:
    name: str
    type: AccountType