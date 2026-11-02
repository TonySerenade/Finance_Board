"""Educational fixed-rate bond analytics; unadjusted coupon dates, ACT/ACT coupon periods.

Yields are nominal annual rates compounded at coupon frequency.
Prices and DV01 are in the same currency as face_value.
No holiday calendar, ex-coupon convention, amortization, callable features or credit model.
"""
from datetime import date
from dataclasses import dataclass
import calendar
from math import isfinite


def _add_months(d: date, months: int) -> date:
    total = d.year * 12 + d.month - 1 + months
    year, month = divmod(total, 12)
    month += 1
    return date(year, month, min(d.day, calendar.monthrange(year, month)[1]))


@dataclass(frozen=True)
class Bond:
    face_value: float
    coupon_rate: float
    maturity_date: date
    frequency: int = 2
    issue_date: date | None = None

    def __post_init__(self):
        if not isfinite(self.face_value) or self.face_value <= 0:
            raise ValueError("Face value must be positive and finite")
        if not isfinite(self.coupon_rate) or self.coupon_rate < 0:
            raise ValueError("Coupon rate must be nonnegative and finite")
        if self.frequency not in (1, 2, 4, 12):
            raise ValueError("Coupon frequency must be 1, 2, 4 or 12")
        if self.issue_date is not None and self.issue_date >= self.maturity_date:
            raise ValueError("Issue date must precede maturity")


def coupon_schedule(bond: Bond, settlement: date):
    """Generate regular coupon dates backwards from maturity (no stub support)."""
    if settlement >= bond.maturity_date:
        raise ValueError("Settlement must precede maturity")
    step = 12 // bond.frequency
    dates = [bond.maturity_date]
    # Anchor dates at maturity to avoid month-end drift.
    n = 1
    while True:
        d = _add_months(bond.maturity_date, -n * step)
        if d <= settlement:
            break
        dates.append(d)
        n += 1
    dates.sort()
    return d, dates


def analyze_bond(bond: Bond, ytm: float, settlement: date) -> dict:
    """Return dirty/clean prices, accrued interest and rate sensitivities.

    ACT/ACT within each coupon period; regular unadjusted coupon schedule.
    Settlement on a coupon date assumes that coupon has already been paid.
    """
    if not isfinite(ytm) or 1 + ytm / bond.frequency <= 0:
        raise ValueError("Yield is outside the valid compounding domain")
    if bond.issue_date is not None and settlement < bond.issue_date:
        raise ValueError("Settlement cannot precede issue date")
    last_coupon, dates = coupon_schedule(bond, settlement)
    next_coupon = dates[0]
    fraction = (settlement - last_coupon).days / (next_coupon - last_coupon).days
    coupon = bond.face_value * bond.coupon_rate / bond.frequency
    accrued = coupon * fraction
    first_exponent = 1 - fraction
    flows = []
    for i, d in enumerate(dates):
        cf = coupon + (bond.face_value if i == len(dates) - 1 else 0)
        flows.append((d, cf, first_exponent + i))

    def dirty_at(y):
        if 1 + y / bond.frequency <= 0:
            raise ValueError("Shock exceeds valid yield domain")
        return sum(cf / (1 + y / bond.frequency) ** exponent
                   for _, cf, exponent in flows)

    dirty = dirty_at(ytm)
    clean = dirty - accrued
    # Analytical sensitivities for the same fractional-period discount model.
    base = 1 + ytm / bond.frequency
    duration_dollars = sum(
        (exponent / bond.frequency) * cf / base ** (exponent + 1)
        for _, cf, exponent in flows
    )
    convexity_dollars = sum(
        exponent * (exponent + 1) / bond.frequency ** 2
        * cf / base ** (exponent + 2)
        for _, cf, exponent in flows
    )
    mod_duration = duration_dollars / dirty
    convexity = convexity_dollars / dirty
    macaulay = mod_duration * base
    return {
        "dirty_price": dirty,
        "clean_price": clean,
        "accrued_interest": accrued,
        "macaulay_duration": macaulay,
        "modified_duration": mod_duration,
        "convexity": convexity,
        "dv01": duration_dollars * 0.0001,
        "cashflows": [{"date": d, "amount": cf, "periods": exp}
                      for d, cf, exp in flows],
        "shock_pnl": lambda bp: dirty_at(ytm + bp / 10000) - dirty,
    }


def price_bond(face_value, coupon_rate, ytm, maturity, frequency=1):
    """Simple textbook pricing for an integer number of complete coupon periods."""
    if not isfinite(maturity) or maturity <= 0:
        raise ValueError("Maturity must be positive")
    n = maturity * frequency
    if abs(n - round(n)) > 1e-9:
        raise ValueError("Maturity must contain whole coupon periods")
    if face_value <= 0 or coupon_rate < 0 or frequency not in (1, 2, 4, 12):
        raise ValueError("Invalid bond inputs")
    if 1 + ytm / frequency <= 0:
        raise ValueError("Invalid yield")
    coupon = face_value * coupon_rate / frequency
    return sum((coupon + (face_value if i == round(n) else 0)) /
               (1 + ytm / frequency) ** i for i in range(1, round(n) + 1))
