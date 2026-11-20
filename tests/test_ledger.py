import unittest

from fund_accounting.ledger import trial_balance


def entry(*postings):
    return {
        "date": "2026-01-01",
        "description": "Test journal entry",
        "postings": [
            {"account": account, "amount": amount} for account, amount in postings
        ],
    }


class TrialBalanceTests(unittest.TestCase):
    def test_aggregates_entries_in_exact_cents(self):
        journal = {
            "currency": "USD",
            "entries": [
                entry(("Cash", "125.50"), ("Partner capital", "-125.50")),
                entry(
                    ("Cash", "-0.30"),
                    ("Management fees", "0.10"),
                    ("Bank charges", "0.20"),
                ),
            ],
        }

        self.assertEqual(
            trial_balance(journal),
            {
                "Cash": 12520,
                "Partner capital": -12550,
                "Management fees": 10,
                "Bank charges": 20,
            },
        )

    def test_empty_journal_has_no_balances(self):
        self.assertEqual(trial_balance({"currency": "USD", "entries": []}), {})

    def test_checks_balance_per_entry(self):
        journal = {
            "currency": "USD",
            "entries": [
                entry(("Cash", "10.01"), ("Partner capital", "-10.00")),
                entry(("Cash", "10.00"), ("Partner capital", "-10.01")),
            ],
        }

        with self.assertRaises(ValueError):
            trial_balance(journal)

    def test_rejects_invalid_amounts(self):
        amount_pairs = (
            (1, "-1.00"),
            (True, "-1.00"),
            (None, "-1.00"),
            ("", "-1.00"),
            ("1.001", "-1.001"),
            ("1e0", "-1.00"),
            ("NaN", "-1.00"),
            ("0.00", "0.00"),
        )
        for amount, opposite in amount_pairs:
            with self.subTest(amount=amount), self.assertRaises(ValueError):
                trial_balance(
                    {
                        "currency": "USD",
                        "entries": [
                            entry(("Cash", amount), ("Partner capital", opposite))
                        ],
                    }
                )

    def test_rejects_invalid_journal_structures(self):
        invalid_journals = (
            None,
            [],
            {},
            {"currency": "USD", "entries": {}},
            {"currency": "EUR", "entries": []},
        )
        for journal in invalid_journals:
            with self.subTest(journal=journal), self.assertRaises(ValueError):
                trial_balance(journal)

    def test_rejects_invalid_entry_structures(self):
        valid_entry = entry(("Cash", "5.00"), ("Partner capital", "-5.00"))
        invalid_entries = (
            None,
            {},
            {**valid_entry, "date": "2026-02-29"},
            {**valid_entry, "description": "   "},
            {**valid_entry, "postings": []},
            entry(("Cash", "5.00")),
            entry(("   ", "5.00"), ("Partner capital", "-5.00")),
        )
        for invalid_entry in invalid_entries:
            with self.subTest(entry=invalid_entry), self.assertRaises(ValueError):
                trial_balance({"currency": "USD", "entries": [invalid_entry]})
