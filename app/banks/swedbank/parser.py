from __future__ import annotations

from datetime import date
from decimal import Decimal
from xml.etree import ElementTree as ET

from app.domain.enums import (
    BankName,
    TransactionDirection,
)
from app.domain.models import (
    Statement,
    Transaction,
)
from app.exceptions import StatementParseError

from .schemas.statement import (
    SwedbankBalance,
    SwedbankStatement,
    SwedbankTransactionRecord,
)


class SwedbankParser:
    """
    Parses bank statement XML into the canonical domain model.

    The parser is intentionally namespace-tolerant because
    ISO 20022 documents can use different namespace prefixes.

    Exact Swedbank XML/CAMT schema validation should be performed
    before calling parse().
    """

    def parse(
        self,
        content: bytes,
        account_iban: str,
    ) -> Statement:
        try:
            root = ET.fromstring(content)
        except ET.ParseError as exc:
            raise StatementParseError(
                "Invalid Swedbank XML document."
            ) from exc

        statement = self._parse_statement(
            root,
            account_iban,
        )

        return self._to_domain(
            statement
        )

    def _parse_statement(
        self,
        root: ET.Element,
        account_iban: str,
    ) -> SwedbankStatement:

        opening = self._find_balance(
            root,
            "OPBD",
        )

        closing = self._find_balance(
            root,
            "CLBD",
        )

        records: list[
            SwedbankTransactionRecord
        ] = []

        for entry in self._find_all(
            root,
            "Ntry",
        ):
            record = self._parse_entry(
                entry
            )

            if record is not None:
                records.append(record)

        return SwedbankStatement(
            account_iban=account_iban,
            opening_balance=opening,
            closing_balance=closing,
            transactions=tuple(records),
        )

    def _parse_entry(
        self,
        entry: ET.Element,
    ) -> SwedbankTransactionRecord | None:

        amount_element = self._find(
            entry,
            "Amt",
        )

        if amount_element is None:
            return None

        amount_text = (
            amount_element.text
        )

        if not amount_text:
            return None

        try:
            amount = Decimal(
                amount_text
            )
        except Exception as exc:
            raise StatementParseError(
                f"Invalid transaction amount: "
                f"{amount_text}"
            ) from exc

        currency = (
            amount_element.attrib.get(
                "Ccy",
                "EUR",
            )
        )

        booking_date = self._find_date(
            entry,
            "BookgDt",
        )

        if booking_date is None:
            raise StatementParseError(
                "Transaction is missing booking date."
            )

        transaction_id = (
            self._find_text(
                entry,
                "InstrId"
            )
            or self._find_text(
                entry,
                "TxId"
            )
            or self._find_text(
                entry,
                "EndToEndId"
            )
        )

        if not transaction_id:
            raise StatementParseError(
                "Transaction is missing transaction ID."
            )

        credit_debit = (
            self._find_text(
                entry,
                "CdtDbtInd",
            )
            or "CRDT"
        )

        debtor_name = self._find_text(
            entry,
            "Dbtr",
        )

        creditor_name = self._find_text(
            entry,
            "Cdtr",
        )

        debtor_iban = self._find_text(
            entry,
            "DbtrAcct",
        )

        creditor_iban = self._find_text(
            entry,
            "CdtrAcct",
        )

        description = (
            self._find_text(
                entry,
                "Ustrd",
            )
            or ""
        )

        reference = self._find_text(
            entry,
            "Ref",
        )

        end_to_end_id = self._find_text(
            entry,
            "EndToEndId",
        )

        return SwedbankTransactionRecord(
            transaction_id=transaction_id,
            booking_date=booking_date,
            value_date=self._find_date(
                entry,
                "ValDt",
            ),
            amount=(
                amount
                if credit_debit == "CRDT"
                else -amount
            ),
            currency=currency,
            debtor_name=debtor_name,
            debtor_iban=debtor_iban,
            creditor_name=creditor_name,
            creditor_iban=creditor_iban,
            description=description,
            reference=reference,
            end_to_end_id=end_to_end_id,
        )

    def _find_balance(
        self,
        root: ET.Element,
        balance_type: str,
    ) -> SwedbankBalance:

        for element in self._find_all(
            root,
            "Bal",
        ):
            code = (
                self._find_text(
                    element,
                    "Cd",
                )
            )

            if code != balance_type:
                continue

            amount_element = self._find(
                element,
                "Amt",
            )

            if amount_element is None:
                continue

            if not amount_element.text:
                continue

            return SwedbankBalance(
                amount=Decimal(
                    amount_element.text
                ),
                currency=amount_element.attrib.get(
                    "Ccy",
                    "EUR",
                ),
            )

        raise StatementParseError(
            f"Missing {balance_type} balance."
        )

    @staticmethod
    def _to_domain(
        statement: SwedbankStatement,
    ) -> Statement:

        transactions: list[
            Transaction
        ] = []

        for record in statement.transactions:

            direction = (
                TransactionDirection.CREDIT
                if record.amount >= 0
                else TransactionDirection.DEBIT
            )

            transactions.append(
                Transaction(
                    bank=BankName.SWEDBANK,
                    account_iban=statement.account_iban,
                    transaction_id=record.transaction_id,
                    booking_date=record.booking_date,
                    value_date=record.value_date,
                    amount=abs(record.amount),
                    currency=record.currency,
                    direction=direction,
                    debtor_name=record.debtor_name,
                    debtor_iban=record.debtor_iban,
                    creditor_name=record.creditor_name,
                    creditor_iban=record.creditor_iban,
                    description=record.description,
                    reference=record.reference,
                    end_to_end_id=record.end_to_end_id,
                )
            )

        return Statement(
            bank=BankName.SWEDBANK,
            account_iban=statement.account_iban,
            opening_balance=statement.opening_balance.amount,
            closing_balance=statement.closing_balance.amount,
            currency=statement.closing_balance.currency,
            transactions=tuple(transactions),
        )

    @staticmethod
    def _find(
        element: ET.Element,
        local_name: str,
    ) -> ET.Element | None:

        for child in element.iter():
            if child.tag.split("}")[-1] == local_name:
                return child

        return None

    @classmethod
    def _find_all(
        cls,
        element: ET.Element,
        local_name: str,
    ) -> list[ET.Element]:

        return [
            child
            for child in element.iter()
            if child.tag.split("}")[-1]
            == local_name
        ]

    @classmethod
    def _find_text(
        cls,
        element: ET.Element,
        local_name: str,
    ) -> str | None:

        found = cls._find(
            element,
            local_name,
        )

        if found is None:
            return None

        if found.text is None:
            return None

        value = found.text.strip()

        return value or None

    @classmethod
    def _find_date(
        cls,
        element: ET.Element,
        local_name: str,
    ) -> date | None:

        value = cls._find_text(
            element,
            local_name,
        )

        if not value:
            return None

        try:
            return date.fromisoformat(
                value[:10]
            )
        except ValueError as exc:
            raise StatementParseError(
                f"Invalid date: {value}"
            ) from exc
