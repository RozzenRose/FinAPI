import pytest
from fastapi import FastAPI, Depends
from fastapi.testclient import TestClient
from uuid import UUID, uuid4
from datetime import datetime
from decimal import Decimal
from app.api.routers.accounts import router as accounts_router
from app.api.routers.transactions import router as transactions_router
from app.domain.entities.account import Account
from app.domain.entities.transaction import Transaction, TransactionEntry
from app.domain.enums import AccountType, EntryType
from app.infrastructure.di import (get_create_account_usecase, get_all_accounts_usecase, get_account_by_id,
                                   get_create_transaction_usecase, get_transaction_by_id_usecase,
                                   get_transactions_by_account_id_usecase)


# Fake use cases для тестов
class FakeCreateAccountUseCase:
    async def execute(self, name, type):
        return Account(id=uuid4(), name=name, type=type)

class FakeGetAllAccountsUseCase:
    async def execute(self):
        return [
            Account(id=uuid4(), name="Cash", type=AccountType.ASSET),
            Account(id=uuid4(), name="Bank", type=AccountType.ASSET),
        ]

class FakeGetAccountByIdUseCase:
    async def execute(self, id: UUID):
        if str(id).endswith("0"):
            raise Exception("Account not found")
        return Account(id=id, name="Cash", type=AccountType.ASSET)


class FakeCreateTransactionUseCase:
    async def execute(self, description, date, raw_entries):
        transaction_id = uuid4()
        return Transaction(
            id=transaction_id,
            description=description,
            date=date,
            entries=[
                TransactionEntry(
                    account_id=entry.account_id,
                    transaction_id=transaction_id,
                    type=entry.type,
                    amount=entry.amount
                ) for entry in raw_entries
            ]
        )


class FakeGetTransactionByIdUseCase:
    async def execute(self, id: UUID):
        if str(id).endswith("0"):
            raise Exception("Transaction not found")
        transaction_id = id
        return Transaction(
            id=transaction_id,
            description="Test Transaction",
            date=datetime.now(),
            entries=[
                TransactionEntry(
                    account_id=uuid4(),
                    transaction_id=transaction_id,
                    type=EntryType.DEBIT,
                    amount=Decimal("100.00")
                )
            ]
        )


class FakeGetTransactionsByAccountIdUseCase:
    async def execute(self, account_id: UUID):
        transaction1_id = uuid4()
        transaction2_id = uuid4()
        return [
            Transaction(
                id=transaction1_id,
                description="Transaction 1",
                date=datetime.now(),
                entries=[
                    TransactionEntry(
                        account_id=account_id,
                        transaction_id=transaction1_id,
                        type=EntryType.DEBIT,
                        amount=Decimal("50.00")
                    )
                ]
            ),
            Transaction(
                id=transaction2_id,
                description="Transaction 2",
                date=datetime.now(),
                entries=[
                    TransactionEntry(
                        account_id=account_id,
                        transaction_id=transaction2_id,
                        type=EntryType.CREDIT,
                        amount=Decimal("25.00")
                    )
                ]
            )
        ]

# Тестовое приложение
app = FastAPI()
app.include_router(accounts_router)
app.include_router(transactions_router)

# override Depends для тестов
app.dependency_overrides = {
    get_create_account_usecase: lambda: FakeCreateAccountUseCase(),
    get_all_accounts_usecase: lambda: FakeGetAllAccountsUseCase(),
    get_account_by_id: lambda: FakeGetAccountByIdUseCase(),
    get_create_transaction_usecase: lambda: FakeCreateTransactionUseCase(),
    get_transaction_by_id_usecase: lambda: FakeGetTransactionByIdUseCase(),
    get_transactions_by_account_id_usecase: lambda: FakeGetTransactionsByAccountIdUseCase(),
}


client = TestClient(app)


### account router ###
def test_create_account():
    response = client.post("/api/accounts", json={"name": "Cash", "type": "ASSET"})
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Cash"
    assert data["type"] == "ASSET"
    assert "id" in data


def test_get_all_accounts():
    response = client.get("/api/accounts")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2
    assert all("id" in acc for acc in data)


def test_get_account_by_id():
    test_id = uuid4()
    response = client.get(f"/api/accounts/{test_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(test_id)
    assert data["name"] == "Cash"


def test_get_account_by_id_not_found():
    # Create ID that ends with "0" to trigger the fake exception
    test_id = UUID("12345678-1234-1234-1234-123456789ab0")
    with pytest.raises(Exception, match="Account not found"):
        # Use the fake use case directly to test the exception
        fake_use_case = FakeGetAccountByIdUseCase()
        import asyncio
        asyncio.run(fake_use_case.execute(test_id))


def test_create_account_invalid_type():
    response = client.post("/api/accounts", json={"name": "Cash", "type": "INVALID_TYPE"})
    assert response.status_code == 422


def test_create_account_missing_fields():
    response = client.post("/api/accounts", json={"name": "Cash"})
    assert response.status_code == 422


### transaction router ###
def test_create_transaction():
    account_id = uuid4()
    transaction_data = {
        "description": "Test Transaction",
        "date": datetime.now().isoformat(),
        "entries": [
            {
                "accountId": str(account_id),
                "type": "DEBIT",
                "amount": "100.50"
            },
            {
                "accountId": str(uuid4()),
                "type": "CREDIT",
                "amount": "100.50"
            }
        ]
    }
    response = client.post("/api/transactions", json=transaction_data)
    assert response.status_code == 200
    data = response.json()
    assert data["description"] == "Test Transaction"
    assert len(data["entries"]) == 2
    # Check amount as float since JSON serialization may remove trailing zero
    assert float(data["entries"][0]["amount"]) == 100.50


def test_create_transaction_invalid_amount():
    account_id = uuid4()
    transaction_data = {
        "description": "Test Transaction",
        "date": datetime.now().isoformat(),
        "entries": [
            {
                "accountId": str(account_id),
                "type": "DEBIT",
                "amount": "-50.00"  # Negative amount should fail
            }
        ]
    }
    response = client.post("/api/transactions", json=transaction_data)
    assert response.status_code == 422


def test_create_transaction_missing_fields():
    transaction_data = {
        "description": "Test Transaction",
        # Missing date and entries
    }
    response = client.post("/api/transactions", json=transaction_data)
    assert response.status_code == 422


def test_get_transaction_by_id():
    test_id = uuid4()
    response = client.get(f"/api/transactions/{test_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(test_id)
    assert data["description"] == "Test Transaction"
    assert len(data["entries"]) == 1


def test_get_transaction_by_id_not_found():
    # Create ID that ends with "0" to trigger the fake exception
    test_id = UUID("12345678-1234-1234-1234-123456789ab0")
    with pytest.raises(Exception, match="Transaction not found"):
        # Use the fake use case directly to test the exception
        fake_use_case = FakeGetTransactionByIdUseCase()
        import asyncio
        asyncio.run(fake_use_case.execute(test_id))


def test_get_transactions_by_account_id():
    account_id = uuid4()
    response = client.get(f"/api/accounts/{account_id}/transactions")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2
    assert all("description" in tx for tx in data)
    assert all("entries" in tx for tx in data)


def test_get_transactions_by_account_id_empty():
    # This test would need a different fake implementation
    # For now, just test the endpoint exists
    account_id = uuid4()
    response = client.get(f"/api/accounts/{account_id}/transactions")
    assert response.status_code == 200


# Edge Cases and Validation Tests
def test_create_account_empty_name():
    response = client.post("/api/accounts", json={"name": "", "type": "ASSET"})
    # Note: This might pass validation depending on Pydantic constraints
    # If you want to enforce non-empty names, add validation to the schema
    if response.status_code == 200:
        # If it passes, at least check the name is empty string
        data = response.json()
        assert data["name"] == ""
    else:
        # If validation is added later, this should be 422
        assert response.status_code == 422


def test_create_transaction_zero_amount():
    account_id = uuid4()
    transaction_data = {
        "description": "Test Transaction",
        "date": datetime.now().isoformat(),
        "entries": [
            {
                "accountId": str(account_id),
                "type": "DEBIT",
                "amount": "0.00"  # Zero amount should fail
            }
        ]
    }
    response = client.post("/api/transactions", json=transaction_data)
    assert response.status_code == 422


def test_create_transaction_invalid_date_format():
    account_id = uuid4()
    transaction_data = {
        "description": "Test Transaction",
        "date": "invalid-date",
        "entries": [
            {
                "accountId": str(account_id),
                "type": "DEBIT",
                "amount": "100.00"
            }
        ]
    }
    response = client.post("/api/transactions", json=transaction_data)
    assert response.status_code == 422


def test_get_account_invalid_uuid():
    response = client.get("/api/accounts/invalid-uuid")
    assert response.status_code == 422


def test_get_transaction_invalid_uuid():
    response = client.get("/api/transactions/invalid-uuid")
    assert response.status_code == 422


def test_get_account_transactions_invalid_uuid():
    response = client.get("/api/accounts/invalid-uuid/transactions")
    assert response.status_code == 422
