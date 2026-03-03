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