from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from .enums import BankName, TransactionDirection


class Transaction(BaseModel):
    model_config = ConfigDict(frozen=True)

    bank: BankName
    account_iban: str

    transaction_id: str
    fingerprint: str | None = None

    booking_date: date
    value_date: date | None = None

    amount: Decimal = Field(decimal_places=2)
    currency: str = Field(min_length=3, max_length=3)

    direction: TransactionDirection

    debtor_name: str | None = None
    debtor_iban: str | None = None

    creditor_name: str | None = None
    creditor_iban: str | None = None

    description: str = ""
    reference: str | None = None
    end_to_end_id: str | None = None

    balance_after: Decimal | None = None

    def with_fingerprint(self, fingerprint: str) -> "Transaction":
        return self.model_copy(
            update={"fingerprint": fingerprint}
        )


class Statement(BaseModel):
    model_config = ConfigDict(frozen=True)

    bank: BankName
    account_iban: str

    opening_balance: Decimal
    closing_balance: Decimal

    currency: str

    transactions: tuple[Transaction, ...]

    statement_id: str | None = None
