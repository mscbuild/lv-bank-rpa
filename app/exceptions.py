class BankRPAError(Exception):
    """Base application exception."""


class ConfigurationError(BankRPAError):
    """Invalid application configuration."""


class BankAPIError(BankRPAError):
    """Bank API error."""


class AuthenticationError(BankRPAError):
    """Bank authentication error."""


class StatementParseError(BankRPAError):
    """Bank statement parsing error."""


class ExportError(BankRPAError):
    """Accounting export error."""
