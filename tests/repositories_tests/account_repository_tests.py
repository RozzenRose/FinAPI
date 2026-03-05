import uuid
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.infrastructure.db.engine import Base
from app.infrastructure.db.models.account import Account as AccountModel
from app.domain.entities.account import Account
from app.domain.enums import AccountType
from app.infrastructure.repositories.account_repository import SqlAlchemyAccountRepo



# Async SQLite in-memory fixtures
@pytest_asyncio.fixture(scope="session")
async def async_engine():
    """Async SQLite in-memory engine."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def session(async_engine):
    async_session = sessionmaker(bind=async_engine,
                                 class_=AsyncSession,
                                 expire_on_commit=False)
    async with async_session() as s:
        yield s


@pytest_asyncio.fixture
async def repo(session) -> SqlAlchemyAccountRepo:
    return SqlAlchemyAccountRepo(session)


async def create_account_model(session, name="TestAccount"):
    account = AccountModel(
        id=uuid.uuid4(),
        name=name,
        type=AccountType.ASSET
    )
    session.add(account)
    await session.commit()
    return account


@pytest.mark.asyncio
async def test_save_and_get_by_id(repo: SqlAlchemyAccountRepo):
    entity = Account(id=uuid.uuid4(), name="MyAccount", type=AccountType.ASSET)
    await repo.save(entity)

    fetched = await repo.get_by_id(entity.id)
    assert fetched is not None
    assert fetched.id == entity.id
    assert fetched.name == entity.name
    assert fetched.type == entity.type


@pytest.mark.asyncio
async def test_get_by_name(repo: SqlAlchemyAccountRepo):
    entity = Account(id=uuid.uuid4(), name="UniqueName", type=AccountType.ASSET)
    await repo.save(entity)

    fetched = await repo.get_by_name("UniqueName")
    assert fetched is not None
    assert fetched.name == "UniqueName"

    missing = await repo.get_by_name("DoesNotExist")
    assert missing is None


@pytest.mark.asyncio
async def test_get_all(repo: SqlAlchemyAccountRepo):
    # Очистка таблицы перед тестом
    all_accounts = await repo.get_all()
    if all_accounts:
        for a in all_accounts:
            model = await repo.session.get(AccountModel, a.id)
            if model:
                await repo.session.delete(model)
        await repo.session.commit()

    # Создаём несколько аккаунтов
    accounts = [
        Account(id=uuid.uuid4(), name=f"Acc{i}", type=AccountType.ASSET)
        for i in range(3)
    ]
    for a in accounts:
        await repo.save(a)

    fetched = await repo.get_all()
    assert len(fetched) == 3
    names = [a.name for a in fetched]
    for i in range(3):
        assert f"Acc{i}" in names


@pytest.mark.asyncio
async def test_get_by_id_not_found(repo: SqlAlchemyAccountRepo):
    missing_id = uuid.uuid4()
    result = await repo.get_by_id(missing_id)
    assert result is None