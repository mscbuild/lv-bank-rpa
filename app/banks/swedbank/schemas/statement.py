from __future__ import annotations

from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class SwedbankBalance(BaseModel):
    """Account balance returned by Swedbank."""

    model_config = ConfigDict(frozen=True)

    amount: Decimal
    currency: str = Field(
        min_length=3,
        max_length=3,
    )


class SwedbankTransactionRecord(BaseModel):
    """Normalized Swedbank transaction record."""

    model_config = ConfigDict(frozen=True)

    transaction_id: str

    booking_date: date
    value_date: date | None = None

    amount: Decimal
    currency: str

    debtor_name: str | None = None
    debtor_iban: str | None = None

    creditor_name: str | None = None
    creditor_iban: str | None = None

    description: str = ""
    reference: str | None = None
    end_to_end_id: str | None = None


class SwedbankStatement(BaseModel):
    """Normalized Swedbank statement."""

    model_config = ConfigDict(frozen=True)

    account_iban: str

    opening_balance: SwedbankBalance
    closing_balance: SwedbankBalance

    transactions: tuple[
        SwedbankTransactionRecord,
        ...
    ]
