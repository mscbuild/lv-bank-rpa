from enum import StrEnum


class BankName(StrEnum):
    SWEDBANK = "swedbank"
    SEB = "seb"


class AccountingProvider(StrEnum):
    ZALKTIS = "zalktis"
    JUMIS = "jumis"


class JobStatus(StrEnum):
    CREATED = "created"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    RECONCILIATION_FAILED = "reconciliation_failed"


class TransactionDirection(StrEnum):
    CREDIT = "credit"
    DEBIT = "debit"
