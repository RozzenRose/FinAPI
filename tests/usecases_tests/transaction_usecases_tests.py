from dataclasses import dataclass
from datetime import datetime
from uuid import uuid4

import pytest

from app.api.schemas.schemas_transaction import CreateTransactionRequest
from app.domain.balance_calculator import BalanceCalculator
from app.domain.entities.account import Account
from app.domain.entities.transaction import Transaction, TransactionEntry
from app.domain.enums import EntryType, AccountType
from app.domain.exceptions import NoDescription, AccountNotFound, TransactionNotFound
from app.services.usecases.transaction_usecases import CreateTransactionUseCase, GetTransactionByIdUseCase, \
    GetTransactionByAccountsIdUseCase
from tests.fake_repositories.fake_account_repo import FakeAccountRepo
from tests.fake_repositories.fake_transaction_repo import FakeTransactionRepo


### CreateTransactionUseCase ###
@dataclass
class CreateTransactionObject:
    account_id = (uuid4())
    transaction_id = uuid4()
    entries_id = (uuid4(), uuid4())
    description = 'Test transaction'
    date = datetime.now()
    debit = EntryType.DEBIT
    credit = EntryType.CREDIT

    entries = [TransactionEntry(id=entries_id[0],
                                account_id=account_id,
                                transaction_id=transaction_id,
                                type=debit,
                                amount=100),
               TransactionEntry(id=entries_id[1],
                                account_id=account_id,
                                transaction_id=transaction_id,
                                type=credit,
                                amount=100)
               ]

    transaction = Transaction(id=transaction_id,
                              description=description,
                              date=date,
                              entries=entries)


@pytest.mark.asyncio
async def test_create_transaction_usecase():
    data = CreateTransactionObject
    trans_repo = FakeTransactionRepo([])
    acc_repo = FakeAccountRepo([Account(id=data.account_id, name='Test account', type=AccountType.ASSET)])

    use_case = CreateTransactionUseCase(transaction_repo=trans_repo,
                                        account_repo=acc_repo)

    answer = await use_case.execute(description=data.description,
                                    date=data.date,
                                    raw_entries=data.entries)

    assert answer.description == data.description
    assert answer.date == data.date


@pytest.mark.asyncio
async def test_create_transaction_nodesctiprion():
    data = CreateTransactionObject()
    data.description = None

    trans_repo = FakeTransactionRepo([])
    acc_repo = FakeAccountRepo([Account(id=data.account_id, name='Test account', type=AccountType.ASSET)])

    use_case = CreateTransactionUseCase(transaction_repo=trans_repo,
                                        account_repo=acc_repo)

    with pytest.raises(NoDescription):
        await use_case.execute(description=data.description,
                               date=data,
                               raw_entries=data.entries)


@pytest.mark.asyncio
async def test_create_transaction_accountnotfound():
    data = CreateTransactionObject()

    trans_repo = FakeTransactionRepo([])
    acc_repo = FakeAccountRepo([])

    use_case = CreateTransactionUseCase(transaction_repo=trans_repo,
                                        account_repo=acc_repo)

    with pytest.raises(AccountNotFound):
        await use_case.execute(description=data.description,
                               date=data,
                               raw_entries=data.entries)


### GetTransactionByIdUseCase ###
@pytest.mark.asyncio
async def test_get_transaction_usecase():
    data = CreateTransactionObject()
    transaction_id = data.transaction_id

    trans_repo = FakeTransactionRepo([data.transaction])

    use_case = GetTransactionByIdUseCase(transaction_repo=trans_repo)

    answer = await use_case.execute(transaction_id)
    assert answer == data.transaction


@pytest.mark.asyncio
async def test_get_transaction_notfound():
    data = CreateTransactionObject()
    transaction_id = uuid4()

    trans_repo = FakeTransactionRepo([data.transaction])

    use_case = GetTransactionByIdUseCase(transaction_repo=trans_repo)

    with pytest.raises(TransactionNotFound):
        await use_case.execute(transaction_id)


### GetTransactionByAccountsIdUseCase ###
@pytest.mark.asyncio
async def test_get_transaction_byaccountid_usecase():
    data = CreateTransactionObject()
    account = Account(id=data.account_id, name='Test account', type=AccountType.ASSET)

    trans_repo = FakeTransactionRepo([data.transaction])
    acc_repo = FakeAccountRepo([account])
    calc = BalanceCalculator()

    use_case = GetTransactionByAccountsIdUseCase(trans_repo, acc_repo, calc)

    answer = await use_case.execute(data.account_id)
    # account
    assert answer[0].type == account.type
    assert answer[0].name == account.name

    # balance calculator
    assert answer[1]['balance'] == calc.calculate(account, [data.transaction])

    # transactions
    assert answer[2] == [data.transaction]
