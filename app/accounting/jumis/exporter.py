from __future__ import annotations

import csv
from io import StringIO
from pathlib import Path

from app.domain.models import Transaction
from app.infrastructure.filesystem import AtomicFileWriter

from .validator import JumisValidator


class JumisExporter:
    """
    Exports normalized bank transactions to a CSV file.

    IMPORTANT:
    This is a canonical CSV exporter. The exact column order,
    delimiter, encoding and fields required by a particular
    Jumis installation must be confirmed against its import
    specification before production use.
    """

    def __init__(
        self,
        validator: JumisValidator | None = None,
    ) -> None:
        self.validator = (
            validator
            or JumisValidator()
        )

    def export(
        self,
        transactions: list[Transaction],
        destination: Path,
    ) -> Path:
        """
        Validate transactions and generate a CSV import file.

        Returns:
            Path to the generated file.
        """

        self.validator.validate_transactions(
            transactions
        )

        output = destination.with_suffix(".csv")

        self.validator.validate_output_path(
            output
        )

        buffer = StringIO(
            newline=""
        )

        writer = csv.writer(
            buffer,
            delimiter=";",
            quotechar='"',
            quoting=csv.QUOTE_MINIMAL,
            lineterminator="\r\n",
        )

        writer.writerow(
            [
                "Bank",
                "AccountIBAN",
                "TransactionID",
                "BookingDate",
                "ValueDate",
                "Amount",
                "Currency",
                "Direction",
                "DebtorName",
                "DebtorIBAN",
                "CreditorName",
                "CreditorIBAN",
                "Description",
                "Reference",
                "EndToEndID",
            ]
        )

        for transaction in transactions:
            writer.writerow(
                [
                    transaction.bank.value,
                    transaction.account_iban,
                    transaction.transaction_id,
                    transaction.booking_date.isoformat(),
                    (
                        transaction.value_date.isoformat()
                        if transaction.value_date
                        else ""
                    ),
                    str(transaction.amount),
                    transaction.currency,
                    transaction.direction.value,
                    transaction.debtor_name or "",
                    transaction.debtor_iban or "",
                    transaction.creditor_name or "",
                    transaction.creditor_iban or "",
                    transaction.description,
                    transaction.reference or "",
                    transaction.end_to_end_id or "",
                ]
            )

        content = buffer.getvalue().encode(
            "utf-8-sig"
        )

        AtomicFileWriter.write(
            output,
            content,
        )

        return output
