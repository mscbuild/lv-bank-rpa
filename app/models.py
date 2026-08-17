from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Optional


@dataclass
class Transaction:
    bank: str
    account_iban: str
    transaction_id: str

    booking_date: date
    value_date: Optional[date]

    amount: Decimal
    currency: str

    debtor_name: Optional[str] = None
    debtor_iban: Optional[str] = None

    creditor_name: Optional[str] = None
    creditor_iban: Optional[str] = None

    description: str = ""

    reference: Optional[str] = None
    end_to_end_id: Optional[str] = None

    balance_after: Optional[Decimal] = None

    @property
    def unique_id(self) -> str:
        return f"{self.bank}:{self.account_iban}:{self.transaction_id}"
