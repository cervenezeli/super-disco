# Super Disco

Super Disco is a starter for a venture capital fund’s accounting ledger. It
validates double-entry journals and calculates a trial balance. The included
example records a fictional capital contribution and a portfolio investment
purchase at cost.

## Run locally

From the repository root, use Python 3.12 or later. The project uses the Python
standard library.

```sh
python3 -m fund_accounting examples/fund-journal.json
python3 -m unittest discover -s tests -v
```

The example produces a USD trial balance with 74,999.50 in Cash, 25,000.50 in
Portfolio investments at cost, and -100,000.00 in Limited partners’ capital.
The signed total is 0.00.

## Journal format

A journal contains a currency of `USD` and a list of entries. Each entry has a
date in `YYYY-MM-DD` format, a description, and at least two postings. Each posting
has an account name and a nonzero amount written as a string with up to two
decimal places. Positive amounts are debits and negative amounts are credits.
Each entry must sum to zero. The ledger uses integer cents throughout.

Use synthetic data in committed examples and tests. Keep private journal files
in the ignored `data/` directory.
