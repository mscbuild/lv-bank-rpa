from decimal import Decimal

from app.domain.models import Statement


class ReconciliationError(Exception):
    pass


def reconcile(statement: Statement) -> None:
    credits = Decimal("0")
    debits = Decimal("0")

    for transaction in statement.transactions:
        if transaction.amount < 0:
            debits += abs(transaction.amount)
        else:
            credits += transaction.amount

    expected = (
        statement.opening_balance
        + credits
        - debits
    )

    if expected != statement.closing_balance:
        raise ReconciliationError(
            "Statement reconciliation failed: "
            f"opening={statement.opening_balance}, "
            f"credits={credits}, "
            f"debits={debits}, "
            f"expected={expected}, "
            f"closing={statement.closing_balance}"
        )
