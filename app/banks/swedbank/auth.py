from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


class SwedbankAuthenticationError(
    RuntimeError
):
    """Raised when Swedbank authentication configuration is invalid."""


@dataclass(frozen=True)
class SwedbankCertificateConfig:
    """
    Client certificate configuration.

    The actual certificate/private-key requirements depend
    on the Swedbank Gateway agreement and technical setup.
    """

    certificate_path: Path
    private_key_path: Path
    private_key_password: str | None = None

    def validate(self) -> None:
        if not self.certificate_path.exists():
            raise SwedbankAuthenticationError(
                "Swedbank certificate does not exist: "
                f"{self.certificate_path}"
            )

        if not self.private_key_path.exists():
            raise SwedbankAuthenticationError(
                "Swedbank private key does not exist: "
                f"{self.private_key_path}"
            )


class SwedbankAuthenticator:
    """
    Provides authentication material for the HTTP client.

    Credentials are intentionally kept outside the source code.
    """

    def __init__(
        self,
        config: SwedbankCertificateConfig,
    ) -> None:
        self.config = config

    def validate(self) -> None:
        self.config.validate()

    def client_certificate(
        self,
    ) -> tuple[str, str]:
        """
        Return certificate and private-key paths.

        httpx can use this tuple for client TLS authentication.
        """

        self.validate()

        return (
            str(self.config.certificate_path),
            str(self.config.private_key_path),
        )
