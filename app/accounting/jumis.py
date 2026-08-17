import csv
from datetime import datetime
from pathlib import Path
from typing import List

from .base import AccountingAdapter
from ..models import Transaction


class JumisAdapter(AccountingAdapter):

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
            f"jumis_bank_"
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
                "Date",
                "Account",
                "Amount",
                "Currency",
                "Counterparty",
                "CounterpartyIBAN",
                "Description",
                "Reference",
                "BankTransactionID",
            ])

            for tx in transactions:

                counterparty = (
                    tx.creditor_name
                    or tx.debtor_name
                    or ""
                )

                counterparty_iban = (
                    tx.creditor_iban
                    or tx.debtor_iban
                    or ""
                )

                writer.writerow([
                    tx.booking_date.isoformat(),
                    tx.account_iban,
                    str(tx.amount),
                    tx.currency,
                    counterparty,
                    counterparty_iban,
                    tx.description,
                    tx.reference or "",
                    tx.transaction_id,
                ])

        return output_file
