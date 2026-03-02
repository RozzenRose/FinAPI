from enum import Enum


class AccountType(str, Enum):
    ASSET = "ASSET"
    LIABILITY = "LIABILITY"
    REVENUE = "REVENUE"
    EXPENSE = "EXPENSE"


class EntryType(str, Enum):
    DEBIT = "DEBIT"
    CREDIT = "CREDIT"