from abc import ABC, abstractmethod
from datetime import date

from app.domain.models import Statement
from app.domain.enums import BankName


class BankAdapter(ABC):

    @property
    @abstractmethod
    def bank_name(self) -> BankName:
        raise NotImplementedError

    @abstractmethod
    def get_statement(
        self,
        account_iban: str,
        date_from: date,
        date_to: date,
    ) -> Statement:
        raise NotImplementedError
