from datetime import date, timedelta
from pathlib import Path

from .database import Database


class Pipeline:

    def __init__(
        self,
        database: Database,
        banks: dict,
        accounting,
        output_dir: Path,
        dry_run: bool = True,
    ):
        self.database = database
        self.banks = banks
        self.accounting = accounting
        self.output_dir = output_dir
        self.dry_run = dry_run

    def run(
        self,
        date_from: date,
        date_to: date,
    ):

        new_transactions = []

        for bank_name, bank_config in self.banks.items():

            adapter = bank_config["adapter"]
            iban = bank_config["iban"]

            print(
                f"[BANK] {bank_name} "
                f"{date_from} -> {date_to}"
            )

            transactions = adapter.get_transactions(
                account_iban=iban,
                date_from=date_from,
                date_to=date_to,
            )

            for transaction in transactions:

                if self.database.exists(transaction):

                    print(
                        f"[SKIP] duplicate "
                        f"{transaction.unique_id}"
                    )

                    continue

                new_transactions.append(transaction)

                print(
                    f"[NEW] "
                    f"{transaction.booking_date} "
                    f"{transaction.amount} "
                    f"{transaction.currency}"
                )

        if not new_transactions:

            print("[INFO] Nothing to import.")
            return None

        print(
            f"[INFO] New transactions: "
            f"{len(new_transactions)}"
        )

        if self.dry_run:

            print(
                "[DRY RUN] Export disabled."
            )

            return new_transactions

        output = self.accounting.export(
            new_transactions,
            self.output_dir
        )

        for transaction in new_transactions:
            self.database.add(transaction)

        print(
            f"[OK] Exported: {output}"
        )

        return output
