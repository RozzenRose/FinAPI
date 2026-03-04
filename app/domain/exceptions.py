class DomainException(Exception):
    status_code = 400
    detail = "Business rule violation"

    def __init__(self, detail: str | None = None):
        if detail:
            self.detail = detail




class AccountAlreadyExists(DomainException):
    status_code = 409
    detail = "Account already exists"

class AccountNotFound(DomainException):
    status_code = 404
    detail = "Account not found"

class WeHaveNotAnyAccounts(DomainException):
    status_code = 404
    detail = "We have not any accounts"

class NoNameAccount(DomainException):
    detail = "Account must be named"




class EntriesQuantityIsWrong(DomainException):
    detail = "The number of entries must be two or more"

class NoCreditEntries(DomainException):
    detail = "There must be at least one CREDIT entries"

class NoDebitEntries(DomainException):
    detail = "There must be at least one DEBIT entries"

class SumOfCreditIsNotPositive(DomainException):
    detail = "Sum of credit entries is not positive"

class SumOfDebitIsNotPositive(DomainException):
    detail = "Sum of debit entries is not positive"

class DebitIsNotEqualCredit(DomainException):
    detail = "Debits is not equal Credits!"
