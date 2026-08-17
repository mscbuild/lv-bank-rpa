import hashlib

from .models import Transaction


def transaction_fingerprint(transaction: Transaction) -> str:
    parts = [
        transaction.bank.value,
        transaction.account_iban,
        transaction.transaction_id,
        transaction.booking_date.isoformat(),
        str(transaction.amount),
        transaction.currency,
        transaction.direction.value,
        transaction.debtor_iban or "",
        transaction.creditor_iban or "",
        transaction.end_to_end_id or "",
        transaction.reference or "",
    ]

    canonical = "|".join(parts)

    return hashlib.sha256(
        canonical.encode("utf-8")
    ).hexdigest()
