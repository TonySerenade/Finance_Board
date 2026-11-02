"""Compact fixed-income terminal. Native Streamlit UI, Python only."""
from datetime import date
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from core.pricing import Bond, analyze_bond

st.set_page_config(page_title="FI | Risk Terminal", page_icon="▦", layout="wide", initial_sidebar_state="expanded")

from core.rates import fetch_sovereign_yields, add_bund_spreads


# Cache network calls for six hours. Streamlit-specific caching belongs in the UI.
@st.cache_data(ttl=21600, show_spinner=False)
def load_yields():
    return add_bund_spreads(fetch_sovereign_yields())


st.markdown(":orange[● FI ANALYTICS] / :blue[MARKET DATA] / :green[RISK ENGINE]")
st.title("FIXED INCOME  /  RISK TERMINAL")
st.caption(f"FIXED INCOME  /  SINGLE NAME ANALYTICS   •   AS OF {date.today():%d %b %Y}")
st.divider()

@st.fragment(run_every="6h")
def sovereign_rates_board():
    """Refresh this market panel while the browser stays connected.

    Streamlit cache avoids repeated downloads between refreshes.
    """
    st.markdown("### :orange[01 /] SOVEREIGN YIELD BOARD")
    st.caption("OECD 10-year benchmark yields via FRED • monthly observations, NOT live trading quotes • cached up to 6h")
    if st.button("Refresh rates", key="refresh_market_rates"):
        load_yields.clear()
    with st.spinner('Loading sovereign yields (up to ~4 seconds)...'):
        rates = load_yields()
        # Keep the last usable rates if the data provider temporarily fails.
        if any(r["value"] is not None for r in rates):
            st.session_state["last_good_rates"] = rates
        elif "last_good_rates" in st.session_state:
            rates = st.session_state["last_good_rates"]
            st.info("FRED unavailable; showing previously loaded rates (check observation dates).")
    if not any(rate['value'] is not None for rate in rates):
        st.warning('Market data unavailable. Bond pricing and risk analytics remain accessible below.')
    columns = st.columns(len(rates), gap="small")
    for column, rate in zip(columns, rates):
        value = rate["value"]
        with column:
            with st.container(border=True):
                st.metric(rate["label"], f"{value:.2f}%" if value is not None else "N/A")
            if rate["spread_bp"] is not None:
                st.caption(f"{rate['spread_bp']:+.0f} bp vs Bund")
            elif rate["region"] == "Bund":
                st.caption("BENCHMARK")
            else:
                st.caption("10Y YIELD" if value is not None else "UNAVAILABLE / STALE")
            st.caption(rate["date"].strftime("%Y-%m") if rate["date"] else "NO DATA")
    st.caption("Source: OECD Main Economic Indicators, distributed by FRED (Federal Reserve Bank of St. Louis). Each tile uses its own latest observation month. Different observation dates may affect cross-country spread comparisons.")
    with st.expander("Source series and observation dates"):
        st.dataframe(pd.DataFrame([
            {"Country": r["label"], "FRED series": r["series_id"], "Observation": str(r["date"]) if r["date"] else "N/A", "Status": "Stale" if r["stale"] else ("OK" if r["value"] is not None else "Unavailable")}
            for r in rates
        ]), hide_index=True, use_container_width=True)
    st.divider()


sovereign_rates_board()

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

st.markdown("### :orange[02 /] INSTRUMENT HEADER")
with st.container(border=True):
    st.markdown(f"**{bond_name or 'UNNAMED SECURITY'}**  |  {issuer or 'UNKNOWN ISSUER'}  |  {isin or 'ISIN NOT SET'}")
    st.caption(f"COUPON {coupon:.2f}%  /  YTM {ytm:.2f}%  /  FACE {face_value:,.2f}  /  MATURITY {maturity_date:%d %b %Y}")
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

st.markdown("### :orange[03 /] PRICING & RISK GRID")
price_cols = st.columns(4, gap="small")
for col, label, key, precision in zip(
    price_cols,
    ["DIRTY PRICE", "CLEAN PRICE", "ACCRUED", "DV01 / BP"],
    ["dirty_price", "clean_price", "accrued_interest", "dv01"],
    [2, 2, 2, 4],
):
    with col:
        with st.container(border=True):
            st.metric(label, f"{analytics[key]:,.{precision}f}")

risk_cols = st.columns(3, gap="small")
for col, label, value in zip(
    risk_cols,
    ["MACAULAY DURATION", "MODIFIED DURATION", "CONVEXITY"],
    [f"{analytics['macaulay_duration']:.3f} Y", f"{analytics['modified_duration']:.3f} Y", f"{analytics['convexity']:.3f}"],
):
    with col:
        with st.container(border=True):
            st.metric(label, value)
st.divider()

st.markdown("### :orange[04 /] RATE SHOCK MONITOR")
# Keep scenario inputs directly above the stress-test results.
with st.container(border=True):
    st.markdown(":orange[SCENARIO CONTROLS]  |  :blue[PARALLEL YIELD SHIFT]")
    shock_control, shock_readout = st.columns([4, 1], vertical_alignment="center")
    with shock_control:
        shock_bp = st.slider("Yield shock (basis points)", -200, 200, 50, 5)
    with shock_readout:
        st.metric("APPLIED SHOCK", f"{shock_bp:+} bp")
    st.caption("Negative shock = falling yields; positive shock = rising yields.")
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
    st.dataframe(
        shocks.style.format("{:+,.4f}").map(
            lambda x: "color: #00D7A0" if x > 0 else ("color: #FF705D" if x < 0 else ""),
            subset=["Exact P&L", "Dur+Conv P&L"],
        ),
        use_container_width=True, height=410,
    )
with right:
    st.metric(f"SELECTED SCENARIO  /  {shock_bp:+} bp", f"{analytics['shock_pnl'](shock_bp):+,.2f}")
    # Color-code profits and losses, just like a trading risk monitor.
    chart = go.Figure(go.Bar(
        x=shocks.index.tolist(),
        y=shocks["Exact P&L"].tolist(),
        marker_color=["#00D7A0" if pnl >= 0 else "#FF705D" for pnl in shocks["Exact P&L"]],
        hovertemplate="Yield shock: %{x:+} bp | P&L: %{y:+,.4f}<extra></extra>",
    ))
    chart.update_layout(
        template="plotly_dark", height=305,
        paper_bgcolor="#080C10", plot_bgcolor="#080C10",
        font=dict(color="#C8D3DF", family="Consolas, monospace"),
        margin=dict(l=10, r=10, t=10, b=10),
        xaxis=dict(title="Shock (bp)", gridcolor="#25313B"),
        yaxis=dict(title="P&L", gridcolor="#25313B"),
        showlegend=False,
    )
    st.plotly_chart(chart, use_container_width=True)
st.caption("All P&L and DV01 figures are in the entered face-value currency. Parallel YTM shifts only; no spread, FX, liquidity or carry effects.")
st.divider()

st.markdown("### :orange[05 /] CASH FLOW LADDER")
flows = pd.DataFrame(analytics["cashflows"])
flows["date"] = flows["date"].astype(str)
flows = flows.rename(columns={"date": "Payment date", "amount": "Cash flow", "periods": "Discount periods"})
st.dataframe(flows, hide_index=True, use_container_width=True, height=290,
             column_config={"Cash flow": st.column_config.NumberColumn(format="%.2f"),
                            "Discount periods": st.column_config.NumberColumn(format="%.3f")})
with st.expander("MODEL CONVENTIONS & LIMITATIONS"):
    st.write("Regular fixed coupons anchored at maturity; unadjusted payment dates and ACT/ACT within coupon periods. No irregular stub coupons, business-day adjustments, embedded options or credit-spread curves. Sovereign rates are OECD monthly benchmarks distributed via FRED, not live quotes.")
