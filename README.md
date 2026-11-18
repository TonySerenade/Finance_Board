# Finance Board — Fixed Income Risk Terminal

A Python-based fixed income analytics dashboard built with **Streamlit**. Finance Board combines single-bond valuation, interest-rate risk analysis, scenario stress testing, and historical sovereign yield monitoring in a terminal-inspired interface.

> **Status:** Personal project under active development. Educational analytics, not a live trading or investment decision system.

## Features

### Bond pricing
- Configure an individual fixed-rate bond: name, issuer, ISIN, face value, coupon, yield to maturity (YTM), issue date, maturity date, and annual or semiannual coupon frequency.
- Generate a schedule of future coupon and principal cash flows.
- Calculate **dirty price**, **clean price**, and **accrued interest** using a discounted cash-flow model.

### Interest-rate risk
- **Macaulay duration** and **modified duration**.
- **DV01** (price sensitivity to a one-basis-point yield change).
- **Convexity** for second-order yield sensitivity.

### Rate Shock Monitor
- Fixed parallel YTM shocks of **±10, ±20, ±30, ±50, and ±100 basis points**.
- Compare **exact repricing P&L** with a **duration-plus-convexity approximation**.
- Inspect approximation errors in a table and P&L in a Plotly bar chart.

### Sovereign Yield Board
- Historical **10-year sovereign benchmark yields** for the US, France, Germany, Spain, Belgium, the UK, and Italy.
- Data sourced from **OECD series distributed via FRED** (monthly observations; **not live quotes**).
- European sovereign yield spreads versus the German Bund.
- Observation dates, stale-data indicators, and source-series diagnostics.
- Streamlit caching for up to **24 hours**, a manual refresh button, and a periodic panel rerun while the app remains connected. Data availability depends on the upstream provider.

## Getting started

Requires **Python 3.10+**.

```bash
git clone https://github.com/TonySerenade/Finance_Board.git
cd Finance_Board
python -m venv .venv
```

Activate the environment:

**Windows (PowerShell):**
```powershell
.venv\Scripts\Activate.ps1
```

**macOS / Linux:**
```bash
source .venv/bin/activate
```

Install dependencies and launch the dashboard:

```bash
pip install -r requirements.txt
streamlit run app.py
```

Open the local address shown by Streamlit (typically `http://localhost:8501`).

## Project architecture

```text
Finance_Board/
├── app.py                 # Streamlit interface, dashboards and charts
├── core/
│   ├── pricing.py         # Bond cash flows, valuation and sensitivities
│   └── rates.py           # Sovereign yield retrieval and Bund spreads
├── requirements.txt       # Python dependencies
└── README.md
```

The pricing engine and market-data logic are separated from the Streamlit presentation layer.

## Model conventions and limitations

- Fixed-rate, bullet bonds with regular coupons; no amortization, callable features, or embedded options.
- Coupon dates are anchored to maturity and are **not business-day adjusted**. No irregular stub coupons or holiday calendars.
- Accrual uses actual days within each coupon period; yields are nominal annual rates compounded at coupon frequency.
- Settlement is assumed to be **today** in the interface. On a coupon date, the coupon is treated as already paid.
- Rate shocks are parallel shifts to the **bond's entered YTM**, not independent curve or credit-spread shocks.
- P&L and DV01 are denominated in the same currency units as the entered face value; no FX, liquidity, carry, or transaction-cost modeling.
- The sovereign board shows **monthly historical benchmarks**, which may be stale or unavailable. Spreads may compare observations from different months.

## Tech stack

**Python · Streamlit · Pandas · Plotly · Requests · FRED/OECD data**

## Roadmap

Potential future enhancements include portfolio-level aggregation, yield-curve-based valuation, additional bond conventions, and richer scenario analysis. These are **not yet implemented**.

---

*Finance Board is a personal learning and portfolio project focused on fixed income pricing, market data, and risk analytics.*
