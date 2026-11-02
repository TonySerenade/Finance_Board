# ============================================================
# BOND ANALYZER
# ============================================================

from datetime import date

import pandas as pd
import streamlit as st
from core.pricing import Bond, analyze_bond


# ============================================================
# 1. TAUX MANUELS
# ============================================================

MANUAL_MARKET_RATES = [
    {"label": "US 10Y", "value": 5.22, "region": "US"},
    {"label": "OAT 10Y", "value": 4.79, "region": "Europe"},
    {"label": "Bund 10Y", "value": 3.57, "region": "Bund"},
    {"label": "Bono 10Y", "value": 4.11, "region": "Europe"},
    {"label": "OLO 10Y", "value": 4.38, "region": "Europe"},
    {"label": "Gilt 10Y", "value": 4.50, "region": "Europe"},
    {"label": "BTP 10Y", "value": 4.59, "region": "Europe"},
]


# ============================================================
# 2. CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Bond Analyzer",
    page_icon="📈",
    layout="wide",
)


# ============================================================
# 3. CSS
# ============================================================

# ============================================================
# 4. CALCUL DES SPREADS
# ============================================================

def calculate_spreads(rates):
    """
    Calcule les spreads européens contre le Bund en points de base.
    """

    bund_rate = None

    for rate in rates:
        if rate["label"] == "Bund 10Y":
            bund_rate = rate["value"]

    result = []

    for rate in rates:

        value = rate["value"]

        if (
            rate["region"] == "Europe"
            and bund_rate is not None
            and value is not None
        ):
            spread = (value - bund_rate) * 100
        else:
            spread = None

        result.append(
            {
                "label": rate["label"],
                "value": value,
                "region": rate["region"],
                "spread": spread,
            }
        )

    return result


# ============================================================
# 5. BANDEAU DE MARCHÉ SANS HTML
# ============================================================

def render_market_banner(rates):
    """
    Affiche les taux sans HTML dynamique.

    On utilise uniquement des composants Streamlit natifs.
    """

    st.subheader("10Y Government Bond Rates & Spreads")
    st.caption("Illustrative manual inputs — NOT live market quotations.")

    columns = st.columns(len(rates))

    for column, rate in zip(columns, rates):

        with column:

            # Chaque taux est placé dans une carte Streamlit native.
            with st.container(border=True):

                st.caption(rate["label"])

                if rate["value"] is None:
                    st.write("Rate: N/A")
                else:
                    st.write(
                        f"Rate: {rate['value']:.2f} %"
                    )

                if rate["label"] == "Bund 10Y":
                    st.write("Reference")

                elif rate["spread"] is None:
                    st.write("Spread: N/A")

                else:
                    st.write(
                        f"Spread: "
                        f"{rate['spread']:+.1f} bp"
                    )


# ============================================================
# 10. TITRE ET BANDEAU
# ============================================================

st.title("📈 Bond Analyzer")
st.caption("Fixed-income pricing and interest-rate risk analytics")

market_data = calculate_spreads(
    MANUAL_MARKET_RATES
)

render_market_banner(market_data)


# ============================================================
# 11. CARTE BOND INPUT
# ============================================================

with st.container(border=True):

    st.subheader("Bond Input")

    # Ligne 1
    row_1_col_1, row_1_col_2, row_1_col_3 = st.columns(3)

    with row_1_col_1:
        isin = st.text_input(
            "ISIN",
            placeholder="Ex: FR001400FYQ4",
        )

    with row_1_col_2:
        bond_name = st.text_input(
            "Bond Name",
            placeholder="Ex: OAT 2.50% 2030",
        )

    with row_1_col_3:
        issuer = st.text_input(
            "Issuer",
            placeholder="Ex: France",
        )

    # Ligne 2
    row_2_col_1, row_2_col_2, row_2_col_3 = st.columns(3)

    with row_2_col_1:
        face_value = st.number_input(
            "Face Value",
            min_value=0.0,
            value=0.0,
            step=100.0,
        )

    with row_2_col_2:
        coupon = st.number_input(
            "Coupon (%)",
            min_value=0.0,
            value=0.0,
            step=0.1,
        )

    with row_2_col_3:
        ytm = st.number_input(
            "Yield to Maturity (%)",
            value=0.0,
            step=0.1,
        )

    # Ligne 3
    row_3_col_1, row_3_col_2, row_3_col_3 = st.columns(3)

    with row_3_col_1:
        issue_date = st.date_input(
            "Issue Date",
            value=date.today(),
        )

    with row_3_col_2:
        maturity_date = st.date_input(
            "Maturity Date",
            value=date.today(),
        )

    with row_3_col_3:
        frequency = st.selectbox(
            "Coupon Frequency",
            options=[1, 2],
            format_func=lambda value: (
                "Annual"
                if value == 1
                else "Semi-Annual"
            ),
        )

    st.write(
        f"Bond: {bond_name if bond_name else '-'}"
    )

    st.write(
        f"ISIN: {isin if isin else '-'} | "
        f"Issuer: {issuer if issuer else '-'}"
    )

    st.write(
        f"Coupon: {coupon:.2f}% | "
        f"Yield: {ytm:.2f}% | "
        f"Maturity: {maturity_date}"
    )


# ============================================================
# 12. VALIDATION
# ============================================================

valid_dates = maturity_date > issue_date
valid_face_value = face_value > 0
valid_coupon = coupon >= 0
valid_ytm = (1 + (ytm / 100) / frequency) > 0

inputs_are_valid = (
    valid_dates
    and valid_face_value
    and valid_coupon
    and valid_ytm
)


# ============================================================
# 13. AFFICHAGE CONDITIONNEL
# ============================================================

if not inputs_are_valid:

    missing_inputs = []

    if not valid_face_value:
        missing_inputs.append("Face Value")

    if not valid_coupon:
        missing_inputs.append("Coupon")

    if not valid_ytm:
        missing_inputs.append("Yield to Maturity")

    if not valid_dates:
        missing_inputs.append(
            "Maturity Date after Issue Date"
        )

    st.info(
        "Complete the following required inputs to display "
        "the bond analytics: "
        + ", ".join(missing_inputs)
        + "."
    )

else:
    settlement = date.today()
    if settlement >= maturity_date:
        st.warning("This bond has matured. Choose a future maturity.")
    elif settlement < issue_date:
        st.warning("Issue date is in the future. Choose an issued bond.")
    else:
        try:
            bond = Bond(
                face_value=face_value,
                coupon_rate=coupon / 100,
                maturity_date=maturity_date,
                frequency=frequency,
                issue_date=issue_date,
            )
            analytics = analyze_bond(bond, ytm / 100, settlement)
        except ValueError as exc:
            st.error(str(exc))
        else:
            st.subheader("Bond Valuation & Risk")
            st.caption("Illustrative fixed-coupon valuation. Unadjusted maturity-anchored coupon dates, ACT/ACT coupon periods; no holiday adjustments or stub coupons.")
            cols = st.columns(4)
            for col, label, key, fmt in zip(
                cols,
                ["Dirty Price", "Accrued Interest", "Clean Price", "DV01"],
                ["dirty_price", "accrued_interest", "clean_price", "dv01"],
                [",.2f", ",.2f", ",.2f", ",.4f"],
            ):
                col.metric(label, format(analytics[key], fmt))

            cols = st.columns(3)
            cols[0].metric("Macaulay Duration", f"{analytics['macaulay_duration']:.3f} years")
            cols[1].metric("Modified Duration", f"{analytics['modified_duration']:.3f} years")
            cols[2].metric("Convexity", f"{analytics['convexity']:.3f}")

            st.subheader("Parallel Yield Shock Scenarios")
            shock_bp = st.slider("Custom shock (bp)", -200, 200, 50, 5)
            shock_levels = sorted(set([-100, -50, -25, 0, 25, 50, 100, shock_bp]))
            shock_rows = []
            for bp in shock_levels:
                exact = analytics["shock_pnl"](bp)
                dy = bp / 10000
                approximation = analytics["dirty_price"] * (
                    -analytics["modified_duration"] * dy
                    + 0.5 * analytics["convexity"] * dy * dy
                )
                shock_rows.append({
                    "Yield shock (bp)": bp,
                    "Exact repricing P&L": round(exact, 4),
                    "Duration-convexity P&L": round(approximation, 4),
                })
            shocks = pd.DataFrame(shock_rows).set_index("Yield shock (bp)")
            st.dataframe(shocks, use_container_width=True)
            st.bar_chart(shocks[["Exact repricing P&L"]])
            st.caption("P&L per entered face value; yield-only scenarios, no carry, credit spread, FX or liquidity effects.")

            st.subheader("Future Cash Flow Schedule")
            flows = pd.DataFrame(analytics["cashflows"])
            flows["date"] = flows["date"].astype(str)
            st.dataframe(flows.rename(columns={"date": "Payment Date", "amount": "Cash Flow", "periods": "Discount Periods"}), hide_index=True, use_container_width=True)
