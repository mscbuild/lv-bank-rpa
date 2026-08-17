import argparse
import logging
from datetime import date, timedelta
from pathlib import Path

from app.config import load_config
from app.logging import configure_logging
from app.persistence.database import Database
from app.persistence.repositories import TransactionRepository
from app.accounting.zalktis.exporter import ZalktisExporter


logger = logging.getLogger(
    "lv-bank-rpa"
)


def build_parser() -> argparse.ArgumentParser:

    parser = argparse.ArgumentParser(
        prog="lv-bank-rpa",
        description=(
            "Latvian bank statement "
            "automation platform"
        ),
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
    )

    sync = subparsers.add_parser(
        "sync",
        help="Synchronize bank statements",
    )

    sync.add_argument(
        "--from",
        dest="date_from",
        type=date.fromisoformat,
    )

    sync.add_argument(
        "--to",
        dest="date_to",
        type=date.fromisoformat,
    )

    sync.add_argument(
        "--dry-run",
        action="store_true",
    )

    health = subparsers.add_parser(
        "health",
        help="Check application health",
    )

    return parser


def main() -> int:

    configure_logging()

    parser = build_parser()
    args = parser.parse_args()

    if args.command == "health":
        print("OK")
        return 0

    if args.command == "sync":

        date_to = (
            args.date_to
            or date.today()
        )

        date_from = (
            args.date_from
            or date_to - timedelta(days=1)
        )

        config = load_config(
            "config/config.example.yaml"
        )

        database = Database(
            config.database.url
        )

        database.create_tables()

        repository = TransactionRepository(
            database
        )

        logger.info(
            "sync requested: %s -> %s",
            date_from,
            date_to,
        )

        if args.dry_run:
            logger.info(
                "dry-run enabled"
            )

        logger.info(
            "database initialized"
        )

        return 0

    parser.error(
        "Unknown command"
    )

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
