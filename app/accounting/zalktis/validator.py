from __future__ import annotations

from decimal import Decimal, InvalidOperation
from pathlib import Path

from app.domain.models import Transaction


class ZalktisValidationError(ValueError):
    """Raised when data is not valid for Zalktis export."""


class ZalktisValidator:
    """
    Validates normalized transactions before they are passed
    to the Zalktis exporter.

    This validator intentionally validates the canonical internal
    transaction model. Exact Zalktis file-format validation should
    additionally be performed against the import schema used by
    the target Zalktis version.
    """

    SUPPORTED_CURRENCIES = {
        "EUR",
    }

    def validate_transaction(
        self,
        transaction: Transaction,
    ) -> None:
        self._validate_account(transaction.account_iban)
        self._validate_currency(transaction.currency)
        self._validate_amount(transaction.amount)
        self._validate_transaction_id(
            transaction.transaction_id
        )
        self._validate_booking_date(
            transaction.booking_date
        )

    def validate_transactions(
        self,
        transactions: list[Transaction],
    ) -> None:
        if not transactions:
            raise ZalktisValidationError(
                "No transactions available for export."
            )

        seen_ids: set[str] = set()

        for transaction in transactions:
            self.validate_transaction(transaction)

            if transaction.transaction_id in seen_ids:
                raise ZalktisValidationError(
                    "Duplicate transaction ID in export batch: "
                    f"{transaction.transaction_id}"
                )

            seen_ids.add(
                transaction.transaction_id
            )

    @staticmethod
    def _validate_account(
        iban: str,
    ) -> None:
        if not iban:
            raise ZalktisValidationError(
                "Account IBAN is required."
            )

        normalized = iban.replace(
            " ",
            "",
        ).upper()

        if not normalized.startswith("LV"):
            raise ZalktisValidationError(
                f"Expected Latvian IBAN, got: {iban}"
            )

        if len(normalized) != 21:
            raise ZalktisValidationError(
                f"Invalid Latvian IBAN length: {iban}"
            )

    @classmethod
    def _validate_currency(
        cls,
        currency: str,
    ) -> None:
        currency = currency.upper()

        if currency not in cls.SUPPORTED_CURRENCIES:
            raise ZalktisValidationError(
                f"Unsupported currency: {currency}"
            )

    @staticmethod
    def _validate_amount(
        amount: Decimal,
    ) -> None:
        if not isinstance(amount, Decimal):
            raise ZalktisValidationError(
                "Amount must be Decimal."
            )

        if not amount.is_finite():
            raise ZalktisValidationError(
                "Amount must be finite."
            )

        if amount == Decimal("0"):
            raise ZalktisValidationError(
                "Zero-value transaction is not allowed."
            )

        try:
            amount.quantize(
                Decimal("0.01")
            )
        except InvalidOperation as exc:
            raise ZalktisValidationError(
                f"Invalid monetary amount: {amount}"
            ) from exc

    @staticmethod
    def _validate_transaction_id(
        transaction_id: str,
    ) -> None:
        if not transaction_id:
            raise ZalktisValidationError(
                "Transaction ID is required."
            )

        if len(transaction_id) > 255:
            raise ZalktisValidationError(
                "Transaction ID is too long."
            )

    @staticmethod
    def _validate_booking_date(
        booking_date,
    ) -> None:
        if booking_date is None:
            raise ZalktisValidationError(
                "Booking date is required."
            )

    @staticmethod
    def validate_output_path(
        destination: Path,
    ) -> None:
        if destination.suffix.lower() not in {
            ".csv",
            ".xml",
        }:
            raise ZalktisValidationError(
                "Zalktis output must be CSV or XML."
            )

        if destination.name.startswith("."):
            raise ZalktisValidationError(
                "Hidden files are not valid export targets."
            )
