import re
from decimal import Decimal

IBAN_RE = re.compile(r"^[A-Z]{2}[0-9]{2}[A-Z0-9]{11,30}$")


def normalize_iban(iban: str) -> str:
    return iban.replace(" ", "").upper()


def validate_iban(iban: str) -> str:
    iban = normalize_iban(iban)

    if not IBAN_RE.match(iban):
        raise ValueError(f"Invalid IBAN format: {iban}")

    # ISO 13616 MOD-97 validation
    rearranged = iban[4:] + iban[:4]

    numeric = ""

    for char in rearranged:
        if char.isdigit():
            numeric += char
        else:
            numeric += str(ord(char) - ord("A") + 10)

    if int(numeric) % 97 != 1:
        raise ValueError(f"Invalid IBAN checksum: {iban}")

    return iban


def validate_amount(amount: Decimal) -> Decimal:
    if not amount.is_finite():
        raise ValueError("Amount must be finite")

    return amount
