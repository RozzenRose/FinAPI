import pytest
from uuid import uuid4
from decimal import Decimal
from datetime import datetime
from pydantic import ValidationError

from app.api.schemas.schemas_transaction import EntryItem, CreateTransactionRequest
from app.domain.enums import EntryType


### EntryItem tests ###
def test_entry_item_valid():
    data = {
        "accountId": uuid4(),
        "type": EntryType.DEBIT,
        "amount": Decimal("123.45")
    }
    entry = EntryItem(**data)
    assert entry.account_id == data["accountId"]
    assert entry.type == EntryType.DEBIT
    assert entry.amount == Decimal("123.45")


def test_entry_item_missing_fields():
    """Empty data"""
    data = {
        "accountId": uuid4()
    }
    with pytest.raises(ValidationError):
        EntryItem(**data)


def test_entry_item_invalid_amount():
    """3 signs after dot"""
    data = {
        "accountId": uuid4(),
        "type": EntryType.CREDIT,
        "amount": Decimal("10.123")
    }
    with pytest.raises(ValidationError):
        EntryItem(**data)


def test_entry_item_invalid_type():
    """invalid type"""
    data = {
        "accountId": uuid4(),
        "type": "INVALID",
        "amount": Decimal("10.00")
    }
    with pytest.raises(ValidationError):
        EntryItem(**data)


### CreateTransactionRequest tests ###
def test_create_transaction_request_valid():
    entries = [
        {
            "accountId": uuid4(),
            "type": EntryType.DEBIT,
            "amount": Decimal("50.00")
        },
        {
            "accountId": uuid4(),
            "type": EntryType.CREDIT,
            "amount": Decimal("50.00")
        }
    ]
    data = {
        "description": "Test transaction",
        "date": datetime.now(),
        "entries": entries
    }

    tx = CreateTransactionRequest(**data)
    assert tx.description == "Test transaction"
    assert len(tx.entries) == 2
    assert tx.entries[0].amount == Decimal("50.00")


def test_create_transaction_request_missing_entries():
    """without entries"""
    data = {
        "description": "Test",
        "date": datetime.now()
    }
    with pytest.raises(ValidationError):
        CreateTransactionRequest(**data)
