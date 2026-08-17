from datetime import datetime

from sqlalchemy import DateTime, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.domain.models import Transaction

from .database import Base, Database


class StoredTransaction(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    fingerprint: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        unique=True,
    )

    bank: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
    )

    account_iban: Mapped[str] = mapped_column(
        String(34),
        nullable=False,
    )

    transaction_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    imported_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    __table_args__ = (
        UniqueConstraint(
            "bank",
            "account_iban",
            "transaction_id",
        ),
    )


class TransactionRepository:

    def __init__(self, database: Database):
        self.database = database

    def exists(self, transaction: Transaction) -> bool:
        from sqlalchemy import select

        with self.database.Session() as session:
            result = session.execute(
                select(StoredTransaction).where(
                    StoredTransaction.fingerprint
                    == transaction.fingerprint
                )
            )

            return result.scalar_one_or_none() is not None

    def save(self, transaction: Transaction) -> None:
        if not transaction.fingerprint:
            raise ValueError(
                "Transaction fingerprint is required"
            )

        with self.database.Session() as session:
            record = StoredTransaction(
                fingerprint=transaction.fingerprint,
                bank=transaction.bank.value,
                account_iban=transaction.account_iban,
                transaction_id=transaction.transaction_id,
            )

            session.add(record)
            session.commit()
