class FinanceManagerError(Exception):
    pass


class ValidationError(FinanceManagerError):
    pass


class InvalidAmountError(ValidationError):
    pass


class InvalidDateError(ValidationError):
    pass


class AuthenticationError(FinanceManagerError):
    pass


class UserNotFoundError(AuthenticationError):
    pass


class TransactionNotFoundError(FinanceManagerError):
    pass


class CategoryNotFoundError(FinanceManagerError):
    pass


class CategoryInUseError(FinanceManagerError):
    pass
