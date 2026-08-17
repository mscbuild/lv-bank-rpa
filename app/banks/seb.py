from datetime import date
from typing import List

import httpx

from .base import BankAdapter
from ..models import Transaction


class SEBAdapter(BankAdapter):

    def __init__(
        self,
        base_url: str,
        client_id: str,
        client_secret: str,
        cert_path: str | None = None,
        key_path: str | None = None,
    ):
        self.base_url = base_url.rstrip("/")
        self.client_id = client_id
        self.client_secret = client_secret

        self.cert = None

        if cert_path and key_path:
            self.cert = (cert_path, key_path)

    def get_access_token(self) -> str:
        """
        Authentication реализуется согласно
        SEB Baltic Gateway/Open Banking specification.
        """

        response = httpx.post(
            f"{self.base_url}/oauth/token",
            data={
                "grant_type": "client_credentials",
            },
            auth=(self.client_id, self.client_secret),
            cert=self.cert,
            timeout=30,
        )

        response.raise_for_status()

        return response.json()["access_token"]

    def get_transactions(
        self,
        account_iban: str,
        date_from: date,
        date_to: date
    ) -> List[Transaction]:

        token = self.get_access_token()

        response = httpx.get(
            f"{self.base_url}/accounts/{account_iban}/transactions",
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/json",
            },
            params={
                "dateFrom": date_from.isoformat(),
                "dateTo": date_to.isoformat(),
            },
            cert=self.cert,
            timeout=60,
        )

        response.raise_for_status()

        return self._parse(
            response.json(),
            account_iban
        )

    def _parse(
        self,
        data,
        account_iban: str
    ) -> List[Transaction]:

        result = []

        for item in data.get("transactions", []):

            result.append(
                Transaction(
                    bank="seb",
                    account_iban=account_iban,
                    transaction_id=str(item["id"]),
                    booking_date=date.fromisoformat(
                        item["bookingDate"]
                    ),
                    value_date=(
                        date.fromisoformat(item["valueDate"])
                        if item.get("valueDate")
                        else None
                    ),
                    amount=item["amount"],
                    currency=item["currency"],
                    debtor_name=item.get("debtorName"),
                    debtor_iban=item.get("debtorIban"),
                    creditor_name=item.get("creditorName"),
                    creditor_iban=item.get("creditorIban"),
                    description=item.get("description", ""),
                    reference=item.get("reference"),
                    end_to_end_id=item.get("endToEndId"),
                )
            )

        return result
