import uuid
import pytest
import pytest_asyncio
from decimal import Decimal
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.infrastructure.db.engine import Base
from app.infrastructure.db.models.account import Account as AccountModel
from app.infrastructure.db.models.transaction import Transaction as TransactionModel
from app.infrastructure.db.models.transaction_entry import TransactionEntry as TransactionEntryModel
from app.domain.entities.transaction import Transaction, TransactionEntry
from app.domain.enums import EntryType, AccountType
from app.infrastructure.repositories.transaction_repository import SqlAlchemyTransactionRepo


# Async SQLite in-memory fixtures
@pytest_asyncio.fixture(scope="session")
async def async_engine():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def session(async_engine):
    async_session = sessionmaker(
        bind=async_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    async with async_session() as s:
        yield s


@pytest_asyncio.fixture
async def repo(session):
    return SqlAlchemyTransactionRepo(session)


async def create_account(session, name="Account1"):
    account = AccountModel(id=uuid.uuid4(), name=name, type=AccountType.ASSET)
    session.add(account)
    await session.commit()
    return account


# Tests
@pytest.mark.asyncio
async def test_create_and_get_transaction(repo, session):
    account = await create_account(session)
    tx_id = uuid.uuid4()
    entry_id = uuid.uuid4()

    transaction = Transaction(
        id=tx_id,
        description="Test Tx",
        date=datetime.now(timezone.utc),
        entries=[
            TransactionEntry(
                id=entry_id,
                account_id=account.id,
                transaction_id=tx_id,
                type=EntryType.DEBIT,
                amount=Decimal("123.45")
            )
        ]
    )

    await repo.create_transaction(transaction)

    fetched = await repo.get_transaction_by_id(tx_id)
    assert fetched is not None
    assert fetched.id == tx_id
    assert len(fetched.entries) == 1
    assert fetched.entries[0].amount == Decimal("123.45")
    assert fetched.entries[0].account_id == account.id


@pytest.mark.asyncio
async def test_get_all_transactions_by_account(repo, session):
    account = await create_account(session, name="TestAccount2")

    # create 2 transaction
    txs = []
    for i in range(2):
        tx_id = uuid.uuid4()
        entry_id = uuid.uuid4()
        tx = Transaction(
            id=tx_id,
            description=f"Tx {i}",
            date=datetime.now(timezone.utc),
            entries=[
                TransactionEntry(
                    id=entry_id,
                    account_id=account.id,
                    transaction_id=tx_id,
                    type=EntryType.CREDIT,
                    amount=Decimal(f"{100+i}")
                )
            ]
        )
        await repo.create_transaction(tx)
        txs.append(tx)

    fetched = await repo.get_all_transaction_by_account_id(account.id)
    assert len(fetched) == 2
    descriptions = [t.description for t in fetched]
    assert "Tx 0" in descriptions
    assert "Tx 1" in descriptions


@pytest.mark.asyncio
async def test_get_transaction_by_id_not_found(repo):
    missing_id = uuid.uuid4()
    result = await repo.get_transaction_by_id(missing_id)
    assert result is None