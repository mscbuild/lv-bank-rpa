import csv
from datetime import datetime
from pathlib import Path
from typing import List

from .base import AccountingAdapter
from ..models import Transaction


class ZalktisAdapter(AccountingAdapter):

    def export(
        self,
        transactions: List[Transaction],
        output_dir: Path
    ) -> Path:

        output_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        filename = (
            f"zalktis_bank_"
            f"{datetime.now():%Y%m%d_%H%M%S}.csv"
        )

        output_file = output_dir / filename

        with output_file.open(
            "w",
            encoding="utf-8-sig",
            newline=""
        ) as file:

            writer = csv.writer(
                file,
                delimiter=";"
            )

            writer.writerow([
                "Bank",
                "IBAN",
                "TransactionID",
                "Date",
                "ValueDate",
                "Amount",
                "Currency",
                "Debtor",
                "DebtorIBAN",
                "Creditor",
                "CreditorIBAN",
                "Description",
                "Reference",
                "EndToEndID",
            ])

            for tx in transactions:

                writer.writerow([
                    tx.bank,
                    tx.account_iban,
                    tx.transaction_id,
                    tx.booking_date.isoformat(),
                    (
                        tx.value_date.isoformat()
                        if tx.value_date
                        else ""
                    ),
                    str(tx.amount),
                    tx.currency,
                    tx.debtor_name or "",
                    tx.debtor_iban or "",
                    tx.creditor_name or "",
                    tx.creditor_iban or "",
                    tx.description,
                    tx.reference or "",
                    tx.end_to_end_id or "",
                ])

        return output_file
