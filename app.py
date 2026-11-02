"""Compact fixed-income terminal. Native Streamlit UI, Python only."""
from datetime import date
import pandas as pd
import streamlit as st
from core.pricing import Bond, analyze_bond

st.set_page_config(page_title="FI | Risk Terminal", page_icon="▦", layout="wide", initial_sidebar_state="expanded")

RATES = [
    ("UST 10Y", 5.22, "US"), ("OAT 10Y", 4.79, "Europe"),
    ("BUND 10Y", 3.57, "Bund"), ("BONO 10Y", 4.11, "Europe"),
    ("OLO 10Y", 4.38, "Europe"), ("GILT 10Y", 4.50, "Europe"),
    ("BTP 10Y", 4.59, "Europe"),
]
BUND = next(rate for label, rate, _ in RATES if label == "BUND 10Y")

st.title("FI  /  BOND RISK TERMINAL")
st.caption(f"FIXED INCOME  /  SINGLE NAME ANALYTICS   •   AS OF {date.today():%d %b %Y}   •   DEMO MARKET RATES (NOT LIVE)")
st.divider()

st.subheader("01  /  SOVEREIGN RATES MONITOR")
columns = st.columns(len(RATES), gap="small")
for column, (label, value, region) in zip(columns, RATES):
    spread = f"{(value - BUND) * 100:+.0f} bp vs Bund" if region == "Europe" else ("BENCHMARK" if region == "Bund" else "10Y YIELD")
    with column:
        st.metric(label, f"{value:.2f}%")
        st.caption(spread)

st.divider()

with st.sidebar:
    st.header("INSTRUMENT SETUP")
    st.caption("01 / SECURITY IDENTIFICATION")
    isin = st.text_input("ISIN", placeholder="FR001400FYQ4")
    bond_name = st.text_input("Security", value="OAT 2.50% 2030")
    issuer = st.text_input("Issuer", value="France")
    st.divider()
    st.caption("02 / CONTRACT TERMS")
    face_value = st.number_input("Face value", min_value=0.01, value=1000.0, step=100.0)
    coupon = st.number_input("Coupon (%)", min_value=0.0, value=2.50, step=0.25)
    ytm = st.number_input("Yield to maturity (%)", value=3.00, step=0.10)
    frequency = st.selectbox("Coupon frequency", [1, 2], index=1, format_func=lambda f: "Annual" if f == 1 else "Semiannual")
    issue_date = st.date_input("Issue date", value=date(2024, 1, 1))
    maturity_date = st.date_input("Maturity date", value=date(2030, 1, 1))
    st.divider()
    st.caption("03 / SCENARIO SETTINGS")
    shock_bp = st.slider("Parallel yield shock (bp)", -200, 200, 50, 5)

st.subheader("02  /  SECURITY SNAPSHOT")
a, b, c, d = st.columns(4, gap="small")
a.metric("SECURITY", bond_name or "—")
b.metric("ISSUER", issuer or "—")
c.metric("YTM", f"{ytm:.2f}%")
d.metric("COUPON", f"{coupon:.2f}%")
st.caption(f"ISIN: {isin or 'NOT SET'}   |   NOTIONAL: {face_value:,.2f}   |   MATURITY: {maturity_date:%d %b %Y}   |   SETTLEMENT: {date.today():%d %b %Y}")
st.divider()

settlement = date.today()
if maturity_date <= issue_date:
    st.error("Maturity must be later than issue date.")
    st.stop()
if maturity_date <= settlement:
    st.error("Bond has matured. Choose a future maturity.")
    st.stop()
if issue_date > settlement:
    st.error("Issue date must not be in the future.")
    st.stop()

try:
    bond = Bond(face_value=face_value, coupon_rate=coupon / 100, maturity_date=maturity_date, frequency=frequency, issue_date=issue_date)
    analytics = analyze_bond(bond, ytm / 100, settlement)
except ValueError as exc:
    st.error(f"Pricing error: {exc}")
    st.stop()

st.subheader("03  /  VALUATION & RISK")
price_cols = st.columns(4, gap="small")
for col, label, key, precision in zip(
    price_cols,
    ["DIRTY PRICE", "CLEAN PRICE", "ACCRUED INTEREST", "DV01"],
    ["dirty_price", "clean_price", "accrued_interest", "dv01"],
    [2, 2, 2, 4],
):
    col.metric(label, f"{analytics[key]:,.{precision}f}")

risk_cols = st.columns(3, gap="small")
risk_cols[0].metric("MACAULAY DURATION", f"{analytics['macaulay_duration']:.3f} y")
risk_cols[1].metric("MODIFIED DURATION", f"{analytics['modified_duration']:.3f} y")
risk_cols[2].metric("CONVEXITY", f"{analytics['convexity']:.3f}")
st.divider()

st.subheader("04  /  RATE SHOCK MONITOR")
left, right = st.columns([1.25, 1], gap="medium")
shock_levels = sorted(set([-200, -100, -50, -25, 0, 25, 50, 100, 200, shock_bp]))
rows = []
for bp in shock_levels:
    dy = bp / 10000
    exact = analytics["shock_pnl"](bp)
    approx = analytics["dirty_price"] * (-analytics["modified_duration"] * dy + 0.5 * analytics["convexity"] * dy ** 2)
    rows.append({"Shock (bp)": bp, "Exact P&L": exact, "Dur+Conv P&L": approx, "Approx error": approx - exact})
shocks = pd.DataFrame(rows).set_index("Shock (bp)")
with left:
    st.caption("EXACT REPRICING VS SECOND-ORDER APPROXIMATION")
    st.dataframe(shocks.style.format("{:+,.4f}"), use_container_width=True, height=410)
with right:
    st.metric(f"SELECTED SCENARIO  /  {shock_bp:+} bp", f"{analytics['shock_pnl'](shock_bp):+,.2f}")
    st.bar_chart(shocks[["Exact P&L"]], height=305)
st.caption("All P&L and DV01 figures are in the entered face-value currency. Parallel YTM shifts only; no spread, FX, liquidity or carry effects.")
st.divider()

st.subheader("05  /  CASH FLOW LADDER")
flows = pd.DataFrame(analytics["cashflows"])
flows["date"] = flows["date"].astype(str)
flows = flows.rename(columns={"date": "Payment date", "amount": "Cash flow", "periods": "Discount periods"})
st.dataframe(flows, hide_index=True, use_container_width=True, height=290,
             column_config={"Cash flow": st.column_config.NumberColumn(format="%.2f"),
                            "Discount periods": st.column_config.NumberColumn(format="%.3f")})
with st.expander("MODEL CONVENTIONS & LIMITATIONS"):
    st.write("Regular fixed coupons anchored at maturity; unadjusted payment dates and ACT/ACT within coupon periods. No irregular stub coupons, business-day adjustments, embedded options or credit-spread curves. Sovereign rate tiles are manually entered illustrative values, not live quotes.")
