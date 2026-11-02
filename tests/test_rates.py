"""Tests for sovereign yield data transformations (no network calls)."""
import unittest
from datetime import date
from unittest.mock import patch, Mock
from core.rates import add_bund_spreads, fetch_sovereign_yields


class RatesTests(unittest.TestCase):
    def test_bund_spreads(self):
        rows = [
            {"label": "BUND 10Y", "region": "Bund", "value": 2.5},
            {"label": "OAT 10Y", "region": "Europe", "value": 3.0},
            {"label": "UST 10Y", "region": "US", "value": 4.0},
        ]
        result = add_bund_spreads(rows)
        self.assertAlmostEqual(result[1]["spread_bp"], 50.0)
        self.assertIsNone(result[0]["spread_bp"])
        self.assertIsNone(result[2]["spread_bp"])

    def test_missing_bund(self):
        result = add_bund_spreads([{"region": "Europe", "value": 3.0}])
        self.assertIsNone(result[0]["spread_bp"])

    @patch("core.rates.SERIES", [("OAT 10Y", "EXAMPLE", "Europe")])
    @patch("core.rates.requests.get")
    def test_fetch_csv_and_stale_flag(self, get):
        response = Mock()
        response.text = "DATE,EXAMPLE\n2026-09-01,3.25\n2026-10-01,3.10\n"
        get.return_value = response
        fresh = fetch_sovereign_yields(as_of=date(2026, 11, 2))
        self.assertAlmostEqual(fresh[0]["value"], 3.10)
        self.assertEqual(fresh[0]["date"], date(2026, 10, 1))
        stale = fetch_sovereign_yields(as_of=date(2027, 2, 1))
        self.assertIsNone(stale[0]["value"])
        self.assertTrue(stale[0]["stale"])


if __name__ == "__main__":
    unittest.main()
