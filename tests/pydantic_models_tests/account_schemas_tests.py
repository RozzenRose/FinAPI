import pytest
from uuid import uuid4
from pydantic import ValidationError
from app.api.schemas.schemas_accounts import CreateAccount
from app.domain.enums import AccountType


def test_create_account_valid():
    """Correct data"""
    data = {
        "name": "My Account",
        "type": AccountType.ASSET
    }
    account = CreateAccount(**data)
    assert account.name == "My Account"
    assert account.type == AccountType.ASSET


def test_create_account_missing_name():
    """No name, ValidationError"""
    data = {
        "type": AccountType.LIABILITY
    }
    with pytest.raises(ValidationError):
        CreateAccount(**data)


def test_create_account_missing_type():
    """No type, ValidationError"""
    data = {
        "name": "Bank"
    }
    with pytest.raises(ValidationError):
        CreateAccount(**data)


def test_create_account_invalid_type():
    """Type is not in AccountType, ValidationError"""
    data = {
        "name": "Cash",
        "type": "INVALID_TYPE"
    }
    with pytest.raises(ValidationError):
        CreateAccount(**data)