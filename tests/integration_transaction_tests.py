from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import AsyncClient, ASGITransport

from app.api.routers.accounts import router as accounts_router
from app.api.routers.transactions import router as transactions_router
from app.config import settings
from app.domain.enums import AccountType
from app.infrastructure.di import get_db

pytestmark = pytest.mark.asyncio


@pytest_asyncio.fixture
async def setup_database():
    """Create database tables and return session factory. Drop all in the end"""
    from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
    from app.infrastructure.db.engine import Base

    engine = create_async_engine(settings.database_tests_url, echo=False)
    session_factory = async_sessionmaker(engine)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield session_factory, engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


#------------------
#TRANSACTION ROUTER
#------------------
### CreateTransaction
async def test_create_transaction_integration(setup_database):
    """Integration test for creating a transaction via POST /api/transactions."""
    session_factory, engine = setup_database

    async with session_factory() as db_session:
        app = FastAPI()
        app.include_router(accounts_router)
        app.include_router(transactions_router)

        async def override_get_db():
            yield db_session

        app.dependency_overrides[get_db] = override_get_db

        async with AsyncClient(transport=ASGITransport(app), base_url="http://testserver") as client:
            accounts_data = [
                {"name": "Cash", "type": "ASSET"},
                {"name": "Food Expense", "type": "EXPENSE"}
            ]

            accounts = []
            for acc_data in accounts_data:
                response = await client.post("/api/accounts", json=acc_data)
                assert response.status_code == 200
                accounts.append(response.json())

            transaction_data = {
                "description": "Lunch payment",
                "date": datetime.now().isoformat(),
                "entries": [
                    {
                        "accountId": accounts[0]["id"],  # Cash (уменьшаем)
                        "type": "CREDIT",  # Для ASSET счета CREDIT означает уменьшение
                        "amount": "25.50"
                    },
                    {
                        "accountId": accounts[1]["id"],  # Food Expense (увеличиваем)
                        "type": "DEBIT",  # Для EXPENSE счета DEBIT означает увеличение
                        "amount": "25.50"
                    }
                ]
            }

            response = await client.post("/api/transactions", json=transaction_data)

            # Check the response
            assert response.status_code == 200
            created_transaction = response.json()

            assert "id" in created_transaction
            assert created_transaction["description"] == transaction_data["description"]
            assert len(created_transaction["entries"]) == 2

            # Check in db
            from sqlalchemy import select
            from app.infrastructure.db.models.transaction import Transaction as TransactionModel
            from app.infrastructure.db.models.transaction_entry import TransactionEntry as EntryModel

            result = await db_session.execute(
                select(TransactionModel).where(TransactionModel.id == UUID(created_transaction["id"]))
            )
            db_transaction = result.scalar_one_or_none()
            assert db_transaction is not None
            assert db_transaction.description == transaction_data["description"]

            result = await db_session.execute(
                select(EntryModel).where(EntryModel.transaction_id == UUID(created_transaction["id"]))
            )
            db_entries = result.scalars().all()
            assert len(db_entries) == 2

            for entry in db_entries:
                assert entry.amount == Decimal("25.50")


async def test_create_transaction_invalid_account_integration(setup_database):
    """Test creating transaction with non-existent account."""
    session_factory, engine = setup_database

    async with session_factory() as db_session:
        app = FastAPI()
        app.include_router(accounts_router)
        app.include_router(transactions_router)

        from fastapi import Request
        from fastapi.responses import JSONResponse
        from app.domain.exceptions import AccountNotFound

        @app.exception_handler(AccountNotFound)
        async def account_not_found_handler(request: Request, exc: AccountNotFound):
            return JSONResponse(
                status_code=404,
                content={"detail": str(exc)}
            )

        async def override_get_db():
            yield db_session

        app.dependency_overrides[get_db] = override_get_db

        async with AsyncClient(transport=ASGITransport(app), base_url="http://testserver") as client:
            real_account_data = {"name": "Real Account", "type": "ASSET"}
            response = await client.post("/api/accounts", json=real_account_data)
            real_account = response.json()

            non_existent_id = uuid4()

            transaction_data = {
                "description": "Transaction with invalid account",
                "date": datetime.now().isoformat(),
                "entries": [
                    {
                        "accountId": str(non_existent_id),  # ureal
                        "type": "DEBIT",
                        "amount": "50.00"
                    },
                    {
                        "accountId": real_account["id"],  # real
                        "type": "CREDIT",
                        "amount": "50.00"
                    }
                ]
            }

            response = await client.post("/api/transactions", json=transaction_data)

            assert response.status_code == 404
            error_data = response.json()
            assert "detail" in error_data
            assert str(non_existent_id) in error_data["detail"]


### GetTransactionById
async def test_get_transaction_by_id_integration(setup_database):
    """Integration test for getting transaction by ID via GET /api/transactions/{id}."""
    session_factory, engine = setup_database

    async with session_factory() as db_session:
        app = FastAPI()
        app.include_router(accounts_router)
        app.include_router(transactions_router)

        async def override_get_db():
            yield db_session

        app.dependency_overrides[get_db] = override_get_db

        async with AsyncClient(transport=ASGITransport(app), base_url="http://testserver") as client:
            # create accounts
            accounts_data = [
                {"name": "Cash", "type": "ASSET"},
                {"name": "Food Expense", "type": "EXPENSE"}
            ]

            accounts = []
            for acc_data in accounts_data:
                response = await client.post("/api/accounts", json=acc_data)
                assert response.status_code == 200
                accounts.append(response.json())

            #create transaction
            transaction_data = {
                "description": "Test transaction for GET by ID",
                "date": datetime.now().isoformat(),
                "entries": [
                    {
                        "accountId": accounts[0]["id"],
                        "type": "CREDIT",
                        "amount": "35.50"
                    },
                    {
                        "accountId": accounts[1]["id"],
                        "type": "DEBIT",
                        "amount": "35.50"
                    }
                ]
            }

            create_response = await client.post("/api/transactions", json=transaction_data)
            assert create_response.status_code == 200
            created_transaction = create_response.json()
            transaction_id = created_transaction["id"]  # Это ID транзакции

            # get transaction by id
            response = await client.get(f"/api/transactions/{transaction_id}")

            # check answer
            assert response.status_code == 200
            transaction = response.json()
            assert transaction["id"] == transaction_id  # Сравниваем ID транзакции
            assert transaction["description"] == transaction_data["description"]
            assert len(transaction["entries"]) == 2

            entries = transaction["entries"]
            assert len(entries) == 2

            # check db
            from sqlalchemy import select
            from app.infrastructure.db.models.transaction import Transaction as TransactionModel
            from app.infrastructure.db.models.transaction_entry import TransactionEntry as EntryModel

            result = await db_session.execute(
                select(TransactionModel).where(TransactionModel.id == UUID(transaction_id))
            )
            db_transaction = result.scalar_one_or_none()
            assert db_transaction is not None
            assert db_transaction.description == transaction_data["description"]
            assert str(db_transaction.id) == transaction_id

            result = await db_session.execute(
                select(EntryModel).where(EntryModel.transaction_id == UUID(transaction_id))
            )
            db_entries = result.scalars().all()
            assert len(db_entries) == 2
            for entry in db_entries:
                assert entry.transaction_id == UUID(transaction_id)


# GetTransactionByAccountID
async def test_get_transactions_by_account_id_integration(setup_database):
    """Integration test for getting transactions by account ID via GET /api/accounts/{account_id}/transactions."""
    session_factory, engine = setup_database

    async with session_factory() as db_session:
        app = FastAPI()
        app.include_router(accounts_router)
        app.include_router(transactions_router)

        async def override_get_db():
            yield db_session

        app.dependency_overrides[get_db] = override_get_db

        async with AsyncClient(transport=ASGITransport(app), base_url="http://testserver") as client:
            # create accounts
            accounts_data = [
                {"name": "Cash", "type": "ASSET"},
                {"name": "Food Expense", "type": "EXPENSE"},
                {"name": "Entertainment", "type": "EXPENSE"}
            ]

            accounts = []
            for acc_data in accounts_data:
                response = await client.post("/api/accounts", json=acc_data)
                assert response.status_code == 200
                accounts.append(response.json())

            # create some trans for Cash
            transaction1_data = {
                "description": "Lunch payment",
                "date": datetime.now().isoformat(),
                "entries": [
                    {
                        "accountId": accounts[0]["id"],  # Cash
                        "type": "CREDIT",
                        "amount": "25.50"
                    },
                    {
                        "accountId": accounts[1]["id"],  # Food Expense
                        "type": "DEBIT",
                        "amount": "25.50"
                    }
                ]
            }

            response = await client.post("/api/transactions", json=transaction1_data)
            assert response.status_code == 200
            transaction1 = response.json()

            transaction2_data = {
                "description": "Movie ticket",
                "date": datetime.now().isoformat(),
                "entries": [
                    {
                        "accountId": accounts[0]["id"],  # Cash
                        "type": "CREDIT",
                        "amount": "15.00"
                    },
                    {
                        "accountId": accounts[2]["id"],  # Entertainment
                        "type": "DEBIT",
                        "amount": "15.00"
                    }
                ]
            }

            response = await client.post("/api/transactions", json=transaction2_data)
            assert response.status_code == 200
            transaction2 = response.json()

            transaction3_data = {
                "description": "Split bill",
                "date": datetime.now().isoformat(),
                "entries": [
                    {
                        "accountId": accounts[1]["id"],  # Food Expense
                        "type": "CREDIT",
                        "amount": "10.00"
                    },
                    {
                        "accountId": accounts[2]["id"],  # Entertainment
                        "type": "DEBIT",
                        "amount": "10.00"
                    }
                ]
            }

            response = await client.post("/api/transactions", json=transaction3_data)
            assert response.status_code == 200
            transaction3 = response.json()

            # get all transactions for Cache
            response = await client.get(f"/api/accounts/{accounts[0]['id']}/transactions")

            # check answer
            assert response.status_code == 200
            result = response.json()

            assert isinstance(result, list)
            assert len(result) == 3

            # first from result [account]
            account_data = result[0]
            assert account_data["id"] == accounts[0]["id"]
            assert account_data["name"] == "Cash"
            assert account_data["type"] == "ASSET"

            # second from result [balance]
            balance_data = result[1]
            assert isinstance(balance_data, dict)
            assert "balance" in balance_data

            assert balance_data["balance"] == -40.5 or balance_data["balance"] == "-40.50"

            # third from result [transactions]
            transactions = result[2]
            assert isinstance(transactions, list)
            assert len(transactions) == 2, f"Expected 2 transactions, got {len(transactions)}"

            # check transactions
            transaction_ids = [t["id"] for t in transactions]
            assert transaction1["id"] in transaction_ids
            assert transaction2["id"] in transaction_ids
            assert transaction3["id"] not in transaction_ids

            # check from DB
            from sqlalchemy import select
            from app.infrastructure.db.models.transaction_entry import TransactionEntry as EntryModel

            result = await db_session.execute(
                select(EntryModel).where(EntryModel.account_id == UUID(accounts[0]["id"]))
            )
            db_entries = result.scalars().all()

            # get uniq transaction_id from entries
            db_transaction_ids = {str(entry.transaction_id) for entry in db_entries}
            assert len(db_transaction_ids) == 2
            assert transaction1["id"] in db_transaction_ids
            assert transaction2["id"] in db_transaction_ids
