from datetime import date

from app.banks.base import BankAdapter
from app.domain.fingerprints import transaction_fingerprint
from app.domain.models import Statement
from app.persistence.repositories import TransactionRepository
from app.services.reconciliation import reconcile


class ImportResult:
    def __init__(self):
        self.total = 0
        self.new = 0
        self.duplicates = 0


class ImportService:

    def __init__(
        self,
        repository: TransactionRepository,
    ):
        self.repository = repository

    def import_statement(
        self,
        adapter: BankAdapter,
        account_iban: str,
        date_from: date,
        date_to: date,
    ) -> tuple[Statement, ImportResult]:

        statement = adapter.get_statement(
            account_iban=account_iban,
            date_from=date_from,
            date_to=date_to,
        )

        reconcile(statement)

        result = ImportResult()

        for transaction in statement.transactions:

            result.total += 1

            fingerprint = transaction_fingerprint(
                transaction
            )

            transaction = transaction.with_fingerprint(
                fingerprint
            )

            if self.repository.exists(transaction):
                result.duplicates += 1
                continue

            self.repository.save(transaction)

            result.new += 1

        return statement, result
