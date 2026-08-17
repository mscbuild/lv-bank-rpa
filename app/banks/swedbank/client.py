from __future__ import annotations

from datetime import date

import httpx

from app.banks.base import BankAdapter
from app.domain.enums import BankName
from app.domain.models import Statement
from app.exceptions import (
    BankAPIError,
    StatementParseError,
)

from .auth import SwedbankAuthenticator
from .parser import SwedbankParser


class SwedbankClient(BankAdapter):
    """
    Swedbank Gateway client.

    The endpoint must be supplied through configuration
    according to the customer's Swedbank Gateway contract.

    No bank-specific endpoint is hardcoded here.
    """

    def __init__(
        self,
        base_url: str,
        authenticator: SwedbankAuthenticator,
        parser: SwedbankParser | None = None,
        timeout: float = 30.0,
    ) -> None:

        if not base_url:
            raise ValueError(
                "Swedbank base URL is required."
            )

        self.base_url = base_url.rstrip(
            "/"
        )

        self.authenticator = authenticator

        self.parser = (
            parser
            or SwedbankParser()
        )

        self.timeout = timeout

    @property
    def bank_name(self) -> BankName:
        return BankName.SWEDBANK

    def get_statement(
        self,
        account_iban: str,
        date_from: date,
        date_to: date,
    ) -> Statement:

        if date_from > date_to:
            raise ValueError(
                "date_from cannot be after date_to."
            )

        certificate = (
            self.authenticator.client_certificate()
        )

        params = {
            "account": account_iban,
            "dateFrom": date_from.isoformat(),
            "dateTo": date_to.isoformat(),
        }

        # The concrete path must come from the
        # Swedbank Gateway technical specification.
        endpoint = self.base_url

        try:
            response = httpx.get(
                endpoint,
                params=params,
                cert=certificate,
                timeout=self.timeout,
                follow_redirects=False,
            )

        except httpx.TimeoutException as exc:
            raise BankAPIError(
                "Swedbank request timed out."
            ) from exc

        except httpx.HTTPError as exc:
            raise BankAPIError(
                "Swedbank HTTP request failed."
            ) from exc

        if response.status_code in {
            401,
            403,
        }:
            raise BankAPIError(
                "Swedbank authentication/authorization failed."
            )

        if response.status_code >= 400:
            raise BankAPIError(
                "Swedbank returned HTTP "
                f"{response.status_code}."
            )

        try:
            return self.parser.parse(
                response.content,
                account_iban=account_iban,
            )

        except StatementParseError:
            raise

        except Exception as exc:
            raise StatementParseError(
                "Unable to parse Swedbank statement."
            ) from exc
