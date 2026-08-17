from abc import ABC, abstractmethod
from pathlib import Path
from typing import List

from ..models import Transaction


class AccountingAdapter(ABC):

    @abstractmethod
    def export(
        self,
        transactions: List[Transaction],
        output_dir: Path
    ) -> Path:
        raise NotImplementedError
