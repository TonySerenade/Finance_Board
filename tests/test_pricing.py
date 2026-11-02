from datetime import date
import unittest

from core.pricing import Bond, analyze_bond, price_bond


class PricingTests(unittest.TestCase):
    def test_textbook_price(self):
        self.assertAlmostEqual(price_bond(1000, 0.05, 0.04, 3), 1027.7509, places=3)

    def test_par_at_coupon_date(self):
        bond = Bond(1000, 0.05, date(2029, 1, 1), 1, date(2024, 1, 1))
        result = analyze_bond(bond, 0.05, date(2027, 1, 1))
        self.assertAlmostEqual(result["dirty_price"], 1000, places=7)
        self.assertAlmostEqual(result["accrued_interest"], 0, places=7)

    def test_clean_dirty_relation(self):
        bond = Bond(1000, 0.06, date(2029, 1, 1), 2, date(2024, 1, 1))
        r = analyze_bond(bond, 0.04, date(2027, 3, 1))
        self.assertAlmostEqual(r["clean_price"] + r["accrued_interest"], r["dirty_price"])
        self.assertGreater(r["accrued_interest"], 0)
        self.assertGreater(r["dv01"], 0)
        self.assertGreater(r["convexity"], 0)
        self.assertLess(r["shock_pnl"](100), 0)

    def test_zero_coupon_and_negative_yield(self):
        r = analyze_bond(Bond(1000, 0, date(2028, 1, 1), 1), -0.01, date(2027, 1, 1))
        self.assertGreater(r["dirty_price"], 1000)

    def test_matured_bond_rejected(self):
        with self.assertRaises(ValueError):
            analyze_bond(Bond(1000, 0.05, date(2027, 1, 1)), 0.04, date(2027, 1, 1))


if __name__ == "__main__":
    unittest.main()
