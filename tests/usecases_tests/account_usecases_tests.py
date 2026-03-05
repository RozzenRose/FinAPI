from uuid import uuid4

import pytest

from app.domain.entities.account import Account
from app.domain.exceptions import NoNameAccount, AccountAlreadyExists, WeHaveNotAnyAccounts, AccountNotFound
from app.services.usecases.account_usecases import CreateAccountUseCase, GetAllAccountsUseCase, GetAccountByIdUseCase
from tests.fake_repositories.fake_account_repo import FakeAccountRepo
from app.domain.enums import AccountType


### CreateAccountUseCase ###
@pytest.mark.asyncio
async def test_create_account_usecase():
    name = 'TEST'
    type = AccountType.ASSET

    repo = FakeAccountRepo([])
    use_case = CreateAccountUseCase(repo)

    account = await use_case.execute(name, type)

    assert isinstance(account, Account)
    assert account.name == name
    assert account.type == type
    assert repo.accounts[0] == account


@pytest.mark.asyncio
async def test_create_account_nonameaccount():
    repo = FakeAccountRepo([])
    use_case = CreateAccountUseCase(repo)
    with pytest.raises(NoNameAccount):
        await use_case.execute('', AccountType.ASSET)


@pytest.mark.asyncio
async def test_create_account_account_exists():
    name = 'TEST'
    type = AccountType.ASSET
    account = Account(name='TEST', type=AccountType.ASSET)
    repo = FakeAccountRepo([account])
    use_case = CreateAccountUseCase(repo)

    with pytest.raises(AccountAlreadyExists):
        await use_case.execute(name, type)


### GetAllAccountsUseCase ###
@pytest.mark.asyncio
async def test_get_all_accounts_usecase():
    names = ('test1', 'test2', 'test3')
    type = AccountType.ASSET
    accounts = [Account(names[0], type), Account(names[1], type), Account(names[2], type)]
    repo = FakeAccountRepo(accounts)
    use_case = GetAllAccountsUseCase(repo)

    answer_accounts = await use_case.execute()

    assert isinstance(accounts, list)
    assert answer_accounts == accounts


@pytest.mark.asyncio
async def test_get_all_accounts_noaccounts():
    repo = FakeAccountRepo([])
    use_case = GetAllAccountsUseCase(repo)

    with pytest.raises(WeHaveNotAnyAccounts):
        await use_case.execute()


### GetAccountByIdUseCase ###
@pytest.mark.asyncio
async def test_get_account_by_id_usecase():
    ids = (uuid4(), uuid4(), uuid4())
    names = ('test1', 'test2', 'test3')
    type = AccountType.ASSET
    accounts = [Account(names[0], type, id=ids[0]),
                Account(names[1], type, id=ids[1]),
                Account(names[2], type, id=ids[2])]
    print(ids[1])
    print(accounts[1].id)
    repo = FakeAccountRepo(accounts)
    use_case = GetAccountByIdUseCase(repo)

    answer = await use_case.execute(ids[1])

    assert isinstance(answer, Account)
    assert answer.id == accounts[1].id
    assert answer.name == accounts[1].name
    assert answer.type == accounts[1].type


@pytest.mark.asyncio
async def test_get_account_by_id_accountnotfound():
    use_case = GetAccountByIdUseCase(FakeAccountRepo([]))

    with pytest.raises(AccountNotFound):
        await use_case.execute(uuid4())
