from datetime import datetime
from decimal import Decimal
from uuid import UUID

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
#ACCOUNT ROUTER
#------------------
### create account ###
async def test_create_account_integration(setup_database):
    session_factory, engine = setup_database

    async with session_factory() as db_session:
        app = FastAPI()
        app.include_router(accounts_router)

        async def override_get_db():
            yield db_session

        app.dependency_overrides[get_db] = override_get_db

        async with AsyncClient(transport=ASGITransport(app), base_url="http://testserver") as client:
            account_data = {
                "name": "Test Cash Account",
                "type": "ASSET"
            }

            response = await client.post("/api/accounts", json=account_data)

            assert response.status_code == 200
            data = response.json()
            assert data["name"] == account_data["name"]
            assert data["type"] == account_data["type"]
            assert "id" in data

            from sqlalchemy import select
            from app.infrastructure.db.models.account import Account as AccountModel

            account_id = data["id"]
            result = await db_session.execute(
                select(AccountModel).where(AccountModel.id == account_id)
            )
            db_account = result.scalar_one_or_none()
            assert db_account is not None
            assert db_account.name == account_data["name"]
            assert db_account.type == AccountType.ASSET


### get_account_by_id ###
async def test_get_all_accounts_integration(setup_database):
    """Integration test for getting all accounts via GET /api/accounts/."""
    session_factory, engine = setup_database

    async with session_factory() as db_session:
        app = FastAPI()
        app.include_router(accounts_router)

        async def override_get_db():
            yield db_session

        app.dependency_overrides[get_db] = override_get_db

        async with AsyncClient(transport=ASGITransport(app), base_url="http://testserver") as client:
            accounts_data = [
                {"name": "Cash Account", "type": "ASSET"},
                {"name": "Credit Card", "type": "LIABILITY"}
            ]

            created_accounts = []
            for account_data in accounts_data:
                response = await client.post("/api/accounts", json=account_data)
                assert response.status_code == 200
                created_accounts.append(response.json())

            # Get all accounts
            response = await client.get("/api/accounts")

            assert response.status_code == 200
            accounts = response.json()

            assert len(accounts) == 2

            # check accounts
            # sort lists for comparing
            accounts_sorted = sorted(accounts, key=lambda x: x["id"])
            created_sorted = sorted(created_accounts, key=lambda x: x["id"])

            for i, account in enumerate(accounts_sorted):
                assert account["id"] == created_sorted[i]["id"]
                assert account["name"] == created_sorted[i]["name"]
                assert account["type"] == created_sorted[i]["type"]


async def test_get_empty_accounts_list_integration(setup_database):
    """Integration test for getting accounts when database is empty."""
    session_factory, engine = setup_database

    async with session_factory() as db_session:
        app = FastAPI()
        app.include_router(accounts_router)

        from fastapi import Request
        from fastapi.responses import JSONResponse
        from app.domain.exceptions import WeHaveNotAnyAccounts

        @app.exception_handler(WeHaveNotAnyAccounts)
        async def we_have_not_any_accounts_handler(request: Request, exc: WeHaveNotAnyAccounts):
            return JSONResponse(
                status_code=404,
                content={"detail": "We have not any accounts"}
            )

        async def override_get_db():
            yield db_session

        app.dependency_overrides[get_db] = override_get_db

        async with AsyncClient(transport=ASGITransport(app), base_url="http://testserver") as client:
            response = await client.get("/api/accounts")

            assert response.status_code == 404
            error_data = response.json()
            assert "detail" in error_data
            assert error_data["detail"] == "We have not any accounts"


### GetAccountByID ###
async def test_get_account_by_id_integration(setup_database):
    """Integration test for getting account by ID via GET /api/accounts/{id}."""
    session_factory, engine = setup_database

    async with session_factory() as db_session:
        app = FastAPI()
        app.include_router(accounts_router)

        async def override_get_db():
            yield db_session

        app.dependency_overrides[get_db] = override_get_db

        async with AsyncClient(transport=ASGITransport(app), base_url="http://testserver") as client:
            # Сначала создаем аккаунт
            account_data = {
                "name": "Test Account by ID",
                "type": "ASSET"
            }

            create_response = await client.post("/api/accounts", json=account_data)
            assert create_response.status_code == 200
            created_account = create_response.json()
            account_id = created_account["id"]

            # Получаем аккаунт по ID
            response = await client.get(f"/api/accounts/{account_id}")

            # Проверяем ответ
            assert response.status_code == 200
            account = response.json()
            assert account["id"] == account_id
            assert account["name"] == account_data["name"]
            assert account["type"] == account_data["type"]

            # Проверка через БД
            from sqlalchemy import select
            from app.infrastructure.db.models.account import Account as AccountModel

            result = await db_session.execute(
                select(AccountModel).where(AccountModel.id == UUID(account_id))
            )
            db_account = result.scalar_one_or_none()
            assert db_account is not None
            assert db_account.name == account_data["name"]
            assert db_account.type == AccountType.ASSET


async def test_get_account_by_nonexistent_id_integration(setup_database):
    """Integration test for getting account with non-existent ID."""
    session_factory, engine = setup_database

    async with session_factory() as db_session:
        app = FastAPI()
        app.include_router(accounts_router)

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
            from uuid import uuid4
            non_existent_id = uuid4()

            response = await client.get(f"/api/accounts/{non_existent_id}")

            assert response.status_code == 404
            error_data = response.json()
            assert "detail" in error_data
            assert error_data["detail"] == f"Account with {non_existent_id} is not found"
