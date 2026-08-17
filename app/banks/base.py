from abc import ABC, abstractmethod
from datetime import date
from typing import List

from ..models import Transaction


class BankAdapter(ABC):

    @abstractmethod
    def get_transactions(
        self,
        account_iban: str,
        date_from: date,
        date_to: date
    ) -> List[Transaction]:
        """
        Получить банковские операции за период.
        """
        raise NotImplementedError
