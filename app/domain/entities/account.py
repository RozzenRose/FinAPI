from dataclasses import dataclass, field
from app.domain.enums import AccountType
from uuid import UUID, uuid4


@dataclass
class Account:
    name: str
    type: AccountType
    id: UUID = field(default_factory=uuid4)