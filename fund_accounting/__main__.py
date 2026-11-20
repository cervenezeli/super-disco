"""Validate a journal and print a trial balance."""

import argparse
import json
import sys
from pathlib import Path

from .ledger import trial_balance


def _format_amount(cents: int) -> str:
    dollars, remainder = divmod(abs(cents), 100)
    sign = "-" if cents < 0 else ""
    return f"{sign}{dollars:,}.{remainder:02d}"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("journal", type=Path, help="path to a USD journal JSON file")
    args = parser.parse_args()

    try:
        with args.journal.open(encoding="utf-8") as source:
            balances = trial_balance(json.load(source))
    except (OSError, ValueError) as error:
        print(f"{args.journal}: {error}", file=sys.stderr)
        return 1

    print("Trial balance (USD)")
    for account, cents in sorted(balances.items()):
        print(f"{account}\t{_format_amount(cents)}")
    print(f"Total\t{_format_amount(sum(balances.values()))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
