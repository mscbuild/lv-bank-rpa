from abc import ABC, abstractmethod
from pathlib import Path

from app.domain.models import Transaction


class AccountingAdapter(ABC):

    @abstractmethod
    def export(
        self,
        transactions: list[Transaction],
        destination: Path,
    ) -> Path:
        raise NotImplementedError

