import uuid
import pytest

from datetime import datetime, UTC
from decimal import Decimal

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.infrastructure.db.engine import Base
from app.infrastructure.db.models import Account, Transaction, TransactionEntry
from app.domain.enums import AccountType, EntryType


@pytest.fixture(scope="session")
def engine():
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    Base.metadata.create_all(engine)

    yield engine

    Base.metadata.drop_all(engine)


@pytest.fixture
def db(engine):
    """Session"""
    Session = sessionmaker(bind=engine)
    session = Session()

    yield session

    session.rollback()
    session.close()


def create_account(db, name=None):
    account = Account(
        id=uuid.uuid4(),
        name=name or f"Account-{uuid.uuid4()}",
        type=AccountType.ASSET,
    )

    db.add(account)
    db.commit()

    return account


def create_transaction(db):
    tx = Transaction(
        id=uuid.uuid4(),
        timestamp=datetime.now(UTC),
        description="Test transaction",
    )

    db.add(tx)
    db.commit()

    return tx


### account model tests ###
def test_create_account(db):
    account = Account(
        id=uuid.uuid4(),
        name=f"Bank-{uuid.uuid4()}",
        type=AccountType.ASSET,
    )

    db.add(account)
    db.commit()

    saved = db.get(Account, account.id)

    assert saved is not None
    assert saved.name.startswith("Bank")
    assert saved.type == AccountType.ASSET


def test_account_name_unique(db):
    name = f"Cash-{uuid.uuid4()}"
    a1 = Account(
        id=uuid.uuid4(),
        name=name,
        type=AccountType.ASSET,
    )
    a2 = Account(
        id=uuid.uuid4(),
        name=name,
        type=AccountType.ASSET
    )

    db.add(a1)
    db.commit()

    db.add(a2)

    with pytest.raises(Exception):
        db.commit()

    # ручной откат, чтобы сессия была чистой
    db.rollback()


### transaction model tests ###
def test_create_transaction(db):
    tx = Transaction(
        id=uuid.uuid4(),
        timestamp=datetime.now(UTC),
        description="Salary payment",
    )

    db.add(tx)
    db.commit()

    saved = db.get(Transaction, tx.id)

    assert saved is not None
    assert saved.description == "Salary payment"


### transaction_entry model tests ###
def test_create_transaction_entry(db):
    account = create_account(db)
    tx = create_transaction(db)

    entry = TransactionEntry(
        id=uuid.uuid4(),
        transaction_id=tx.id,
        account_id=account.id,
        type=EntryType.DEBIT,
        amount=Decimal("100.00"),
    )

    db.add(entry)
    db.commit()

    saved = db.get(TransactionEntry, entry.id)

    assert saved is not None
    assert saved.amount == Decimal("100.00")
    assert saved.account_id == account.id
    assert saved.transaction_id == tx.id


### relationships tests ###
def test_relationship_transaction_entries(db):
    account = create_account(db)
    tx = create_transaction(db)

    entry = TransactionEntry(
        id=uuid.uuid4(),
        transaction_id=tx.id,
        account_id=account.id,
        type=EntryType.DEBIT,
        amount=Decimal("50.00"),
    )

    db.add(entry)
    db.commit()

    db.refresh(tx)

    assert len(tx.entries) == 1
    assert tx.entries[0].amount == Decimal("50.00")


def test_relationship_account_entries(db):
    account = create_account(db)
    tx = create_transaction(db)

    entry = TransactionEntry(
        id=uuid.uuid4(),
        transaction_id=tx.id,
        account_id=account.id,
        type=EntryType.CREDIT,
        amount=Decimal("75.00"),
    )

    db.add(entry)
    db.commit()

    db.refresh(account)

    assert len(account.entries) == 1
    assert account.entries[0].amount == Decimal("75.00")


def test_transaction_cascade_delete(db):
    account = create_account(db)
    tx = create_transaction(db)

    entry = TransactionEntry(
        id=uuid.uuid4(),
        transaction_id=tx.id,
        account_id=account.id,
        type=EntryType.DEBIT,
        amount=Decimal("20.00"),
    )

    db.add(entry)
    db.commit()

    db.delete(tx)
    db.commit()

    result = db.get(TransactionEntry, entry.id)

    assert result is None