import sqlite3
from pathlib import Path

from .models import Transaction


class Database:
    def __init__(self, path: str):
        Path(path).parent.mkdir(parents=True, exist_ok=True)

        self.connection = sqlite3.connect(path)
        self.connection.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                unique_id TEXT PRIMARY KEY,
                bank TEXT NOT NULL,
                account_iban TEXT NOT NULL,
                transaction_id TEXT NOT NULL,
                booking_date TEXT NOT NULL,
                amount TEXT NOT NULL,
                currency TEXT NOT NULL,
                imported_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.connection.commit()

    def exists(self, transaction: Transaction) -> bool:
        cursor = self.connection.execute(
            "SELECT 1 FROM transactions WHERE unique_id = ?",
            (transaction.unique_id,)
        )

        return cursor.fetchone() is not None

    def add(self, transaction: Transaction) -> None:
        self.connection.execute("""
            INSERT OR IGNORE INTO transactions (
                unique_id,
                bank,
                account_iban,
                transaction_id,
                booking_date,
                amount,
                currency
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            transaction.unique_id,
            transaction.bank,
            transaction.account_iban,
            transaction.transaction_id,
            transaction.booking_date.isoformat(),
            str(transaction.amount),
            transaction.currency
        ))

        self.connection.commit()
