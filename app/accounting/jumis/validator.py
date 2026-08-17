from __future__ import annotations

from decimal import Decimal

from app.domain.models import Transaction


class JumisValidationError(ValueError):
    """Raised when transaction data is invalid for Jumis export."""


class JumisValidator:
    """
    Validates canonical transactions before Jumis export.

    This validates the internal domain model.
    Exact Jumis import-format validation should be implemented
    according to the format supported by the target Jumis version.
    """

    SUPPORTED_CURRENCIES = {"EUR"}

    def validate_transaction(
        self,
        transaction: Transaction,
    ) -> None:
        self._validate_iban(
            transaction.account_iban
        )
        self._validate_currency(
            transaction.currency
        )
        self._validate_amount(
            transaction.amount
        )
        self._validate_transaction_id(
            transaction.transaction_id
        )

        if transaction.booking_date is None:
            raise JumisValidationError(
                "Booking date is required."
            )

    def validate_transactions(
        self,
        transactions: list[Transaction],
    ) -> None:
        if not transactions:
            raise JumisValidationError(
                "No transactions available for export."
            )

        transaction_ids: set[str] = set()

        for transaction in transactions:
            self.validate_transaction(
                transaction
            )

            if transaction.transaction_id in transaction_ids:
                raise JumisValidationError(
                    "Duplicate transaction ID: "
                    f"{transaction.transaction_id}"
                )

            transaction_ids.add(
                transaction.transaction_id
            )

    @staticmethod
    def _validate_iban(
        iban: str,
    ) -> None:
        if not iban:
            raise JumisValidationError(
                "Account IBAN is required."
            )

        normalized = (
            iban
            .replace(" ", "")
            .upper()
        )

        if not normalized.startswith("LV"):
            raise JumisValidationError(
                f"Expected Latvian IBAN: {iban}"
            )

        if len(normalized) != 21:
            raise JumisValidationError(
                f"Invalid Latvian IBAN length: {iban}"
            )

    @classmethod
    def _validate_currency(
        cls,
        currency: str,
    ) -> None:
        if currency.upper() not in cls.SUPPORTED_CURRENCIES:
            raise JumisValidationError(
                f"Unsupported currency: {currency}"
            )

    @staticmethod
    def _validate_amount(
        amount: Decimal,
    ) -> None:
        if not isinstance(amount, Decimal):
            raise JumisValidationError(
                "Amount must be Decimal."
            )

        if not amount.is_finite():
            raise JumisValidationError(
                "Amount must be finite."
            )

        if amount == Decimal("0"):
            raise JumisValidationError(
                "Transaction amount cannot be zero."
            )

    @staticmethod
    def _validate_transaction_id(
        transaction_id: str,
    ) -> None:
        if not transaction_id:
            raise JumisValidationError(
                "Transaction ID is required."
            )

        if len(transaction_id) > 255:
            raise JumisValidationError(
                "Transaction ID is too long."
            )
