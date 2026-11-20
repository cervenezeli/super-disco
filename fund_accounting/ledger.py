"""Read a USD journal and calculate account balances in cents."""

import re
from datetime import date


def _amount_in_cents(value: object) -> int:
    if not isinstance(value, str):
        raise ValueError("posting amount must be a decimal string")
    match = re.fullmatch(r"([+-]?)([0-9]+)(?:\.([0-9]{1,2}))?", value)
    if match is None:
        raise ValueError("posting amount must have at most two decimal places")
    sign, dollars, fraction = match.groups()
    cents = int(dollars) * 100 + int((fraction or "").ljust(2, "0"))
    if cents == 0:
        raise ValueError("posting amount must be nonzero")
    return -cents if sign == "-" else cents


def _entry_postings(entry: object) -> list[tuple[str, int]]:
    if not isinstance(entry, dict):
        raise ValueError("entry must be an object")
    entry_date = entry.get("date")
    if not isinstance(entry_date, str) or not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", entry_date):
        raise ValueError("entry date must use YYYY-MM-DD")
    try:
        date.fromisoformat(entry_date)
    except ValueError as error:
        raise ValueError("entry date must be a valid calendar date") from error

    description = entry.get("description")
    if not isinstance(description, str) or not description.strip():
        raise ValueError("entry must have a description")
    postings = entry.get("postings")
    if not isinstance(postings, list) or len(postings) < 2:
        raise ValueError("entry must have at least two postings")

    amounts = []
    for posting in postings:
        if not isinstance(posting, dict):
            raise ValueError("posting must be an object")
        account = posting.get("account")
        if not isinstance(account, str) or not account.strip():
            raise ValueError("posting must have an account name")
        amounts.append((account.strip(), _amount_in_cents(posting.get("amount"))))
    if sum(amount for _, amount in amounts) != 0:
        raise ValueError("debits and credits must balance")
    return amounts


def trial_balance(journal: object) -> dict[str, int]:
    """Return signed account balances, where positive balances are debits."""
    if not isinstance(journal, dict) or journal.get("currency") != "USD":
        raise ValueError("journal must be an object with currency USD")
    entries = journal.get("entries")
    if not isinstance(entries, list):
        raise ValueError("journal must contain an entries list")

    balances: dict[str, int] = {}
    for number, entry in enumerate(entries, start=1):
        try:
            postings = _entry_postings(entry)
        except ValueError as error:
            raise ValueError(f"entry {number}: {error}") from error
        for account, amount in postings:
            balances[account] = balances.get(account, 0) + amount
    return balances
