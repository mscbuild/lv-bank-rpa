import argparse
from datetime import date, timedelta
from pathlib import Path

import yaml

from app.database import Database
from app.pipeline import Pipeline

from app.banks.swedbank import SwedbankAdapter
from app.banks.seb import SEBAdapter

from app.accounting.zalktis import ZalktisAdapter
from app.accounting.jumis import JumisAdapter


def load_config():
    with open(
        "config.yaml",
        "r",
        encoding="utf-8"
    ) as file:
        return yaml.safe_load(file)


def build_pipeline(config):

    db = Database(
        "./data/rpa.sqlite3"
    )

    banks = {}

    for bank in config["banks"]:

        if not bank.get("enabled"):
            continue

        name = bank["name"]

        if name == "swedbank":

            adapter = SwedbankAdapter(
                base_url="https://REPLACE_WITH_BANK_ENDPOINT",
                client_id="REPLACE",
                client_secret="REPLACE",
            )

        elif name == "seb":

            adapter = SEBAdapter(
                base_url="https://REPLACE_WITH_BANK_ENDPOINT",
                client_id="REPLACE",
                client_secret="REPLACE",
            )

        else:
            raise ValueError(
                f"Unknown bank: {name}"
            )

        banks[name] = {
            "adapter": adapter,
            "iban": bank["iban"],
        }

    accounting_name = (
        config["accounting"]["target"]
    )

    if accounting_name == "zalktis":

        accounting = ZalktisAdapter()

        output_dir = Path(
            config["accounting"]
            ["zalktis"]
            ["export_dir"]
        )

    elif accounting_name == "jumis":

        accounting = JumisAdapter()

        output_dir = Path(
            config["accounting"]
            ["jumis"]
            ["export_dir"]
        )

    else:
        raise ValueError(
            f"Unknown accounting system: "
            f"{accounting_name}"
        )

    return Pipeline(
        database=db,
        banks=banks,
        accounting=accounting,
        output_dir=output_dir,
        dry_run=config["pipeline"]["dry_run"],
    )


def main():

    parser = argparse.ArgumentParser(
        description="Latvia Bank → Accounting RPA"
    )

    parser.add_argument(
        "--from",
        dest="date_from",
        help="YYYY-MM-DD"
    )

    parser.add_argument(
        "--to",
        dest="date_to",
        help="YYYY-MM-DD"
    )

    args = parser.parse_args()

    config = load_config()

    if args.date_from:
        date_from = date.fromisoformat(
            args.date_from
        )
    else:
        date_from = date.today() - timedelta(days=1)

    if args.date_to:
        date_to = date.fromisoformat(
            args.date_to
        )
    else:
        date_to = date.today()

    pipeline = build_pipeline(config)

    pipeline.run(
        date_from=date_from,
        date_to=date_to,
    )


if __name__ == "__main__":
    main()
