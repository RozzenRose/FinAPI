import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import AsyncClient, ASGITransport

from app.api.routers.accounts import router as accounts_router
from app.config import settings
from app.domain.enums import AccountType
from app.infrastructure.di import get_db

pytestmark = pytest.mark.asyncio


@pytest_asyncio.fixture
async def setup_database():
    """Create database tables and return session factory. Drop all in the end"""
    from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
    from app.infrastructure.db.engine import Base

    engine = create_async_engine(settings.database_url, echo=False)
    session_factory = async_sessionmaker(engine)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield session_factory, engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


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
