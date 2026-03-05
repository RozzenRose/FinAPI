import pytest
from uuid import uuid4
from decimal import Decimal
from app.domain.entities.transaction import Transaction, TransactionEntry
from app.domain.balance_calculator import BalanceCalculator
from app.domain.exceptions import (EntriesQuantityIsWrong,
                                   NoDebitEntries,
                                   NoCreditEntries,
                                   DebitIsNotEqualCredit, AmountCantBeNegative)
from app.domain.enums import AccountType, EntryType


def test_balance_calculator_assets():
    account_id = uuid4()
    transactions = [
        Transaction(
            description="Deposit",
            date="2026-03-04T16:53:11.540Z",
            entries=[TransactionEntry(transaction_id=uuid4(),
                                      account_id=account_id,
                                      amount=100,
                                      type=EntryType.DEBIT)]
        ),
        Transaction(
            description="Payment",
            date="2026-03-04T16:53:11.540Z",
            entries=[TransactionEntry(transaction_id=uuid4(),
                                      account_id=account_id,
                                      amount=30,
                                      type=EntryType.CREDIT)]
        )
    ]
    account = type('Account', (), {'id': account_id, 'name': 'test', 'type': AccountType.ASSET})
    calc = BalanceCalculator()
    assert calc.calculate(account, transactions) == Decimal(70)


def test_transaction_validate_one_transaction():
    account_id = uuid4()
    transaction = Transaction(
            description="Deposit",
            date="2026-03-04T16:53:11.540Z",
            entries=[TransactionEntry(transaction_id=uuid4(), account_id=account_id,
                                      amount=100, type=EntryType.DEBIT)]
        )
    with pytest.raises(EntriesQuantityIsWrong):
        transaction.validate()


def test_transaction_validate_debit_not_exists():
    account_id = uuid4()
    transaction = Transaction(
            description="Deposit",
            date="2026-03-04T16:53:11.540Z",
            entries=[TransactionEntry(transaction_id=uuid4(), account_id=account_id,
                                      amount=100, type=EntryType.CREDIT),
                     TransactionEntry(transaction_id=uuid4(), account_id=account_id,
                                      amount=100, type=EntryType.CREDIT)]
        )
    with pytest.raises(NoDebitEntries):
        transaction.validate()


def test_transaction_validate_credit_not_exists():
    account_id = uuid4()
    transaction = Transaction(
            description="Deposit",
            date="2026-03-04T16:53:11.540Z",
            entries=[TransactionEntry(transaction_id=uuid4(), account_id=account_id,
                                      amount=100, type=EntryType.DEBIT),
                     TransactionEntry(transaction_id=uuid4(), account_id=account_id,
                                      amount=100, type=EntryType.DEBIT)]
        )
    with pytest.raises(NoCreditEntries):
        transaction.validate()


def test_transaction_validate_credits_not_equal_debits():
    account_id = uuid4()
    transaction = Transaction(
            description="Deposit",
            date="2026-03-04T16:53:11.540Z",
            entries=[TransactionEntry(transaction_id=uuid4(), account_id=account_id,
                                      amount=100, type=EntryType.DEBIT),
                     TransactionEntry(transaction_id=uuid4(), account_id=account_id,
                                      amount=200, type=EntryType.CREDIT)]
        )
    with pytest.raises(DebitIsNotEqualCredit):
        transaction.validate()


def test_transaction_validate_credits_amount_negative():
    account_id = uuid4()
    transaction = Transaction(
            description="Deposit",
            date="2026-03-04T16:53:11.540Z",
            entries=[TransactionEntry(transaction_id=uuid4(), account_id=account_id,
                                      amount=-100, type=EntryType.DEBIT),
                     TransactionEntry(transaction_id=uuid4(), account_id=account_id,
                                      amount=200, type=EntryType.CREDIT)]
        )
    with pytest.raises(AmountCantBeNegative):
        transaction.validate()

