import csv
from pathlib import Path

from app.domain.models import Transaction
from app.infrastructure.filesystem import AtomicFileWriter


class ZalktisExporter:

    def export(
        self,
        transactions: list[Transaction],
        destination: Path,
    ) -> Path:

        rows = []

        header = [
            "bank",
            "account_iban",
            "transaction_id",
            "booking_date",
            "value_date",
            "amount",
            "currency",
            "direction",
            "debtor_name",
            "debtor_iban",
            "creditor_name",
            "creditor_iban",
            "description",
            "reference",
            "end_to_end_id",
        ]

        rows.append(header)

        for transaction in transactions:
            rows.append(
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

        output = destination.with_suffix(".csv")

        from io import StringIO

        buffer = StringIO(
            newline=""
        )

        writer = csv.writer(
            buffer,
            delimiter=";",
            lineterminator="\r\n",
        )

        writer.writerows(rows)

        AtomicFileWriter.write(
            output,
            buffer.getvalue().encode(
                "utf-8-sig"
            ),
        )

        return output
