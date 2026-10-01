# ============================================================
# BOND ANALYZER
# ============================================================
# Application Streamlit d'analyse individuelle d'une obligation.
#
# Fonctionnalités :
# - Bandeau manuel des taux souverains 10 ans
# - Spread des souverains européens contre le Bund
# - Saisie des caractéristiques d'une obligation
# - Duration
# - Modified Duration
# - DV01
# - Cash flows
# - Flux passés grisés
# ============================================================


# ============================================================
# 1. IMPORTS
# ============================================================

import html
from datetime import date

import pandas as pd
import streamlit as st


# ============================================================
# 2. TAUX DE MARCHÉ À METTRE À JOUR MANUELLEMENT
# ============================================================
# Modifie uniquement les valeurs "value".
#
# Les taux sont exprimés en pourcentage :
# 5.22 signifie 5,22 %.
#
# Les spreads contre le Bund sont calculés automatiquement
# pour les obligations européennes.
# ============================================================

MANUAL_MARKET_RATES = [
    {
        "label": "US 10Y",
        "value": 5.22,
        "region": "US",
    },
    {
        "label": "OAT 10Y",
        "value": 4.79,
        "region": "Europe",
    },
    {
        "label": "Bund 10Y",
        "value": 3.57,
        "region": "Bund",
    },
    {
        "label": "Bono 10Y",
        "value": 4.11,
        "region": "Europe",
    },
    {
        "label": "OLO 10Y",
        "value": 4.38,
        "region": "Europe",
    },
    {
        "label": "Gilt 10Y",
        "value": 4.50,
        "region": "Europe",
    },
    {
        "label": "BTP 10Y",
        "value": 4.59,
        "region": "Europe",
    },
]


# ============================================================
# 3. CONFIGURATION STREAMLIT
# ============================================================

st.set_page_config(
    page_title="Bond Analyzer",
    page_icon="📈",
    layout="wide",
)


# ============================================================
# 4. CSS GLOBAL
# ============================================================

st.markdown(
    """
    <style>
        .stApp {
            background-color: #0b0f14;
            color: #e5e7eb;
        }

        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }

        div[data-testid="stVerticalBlockBorderWrapper"] {
            background-color: #111827;
            border: 1px solid #374151;
            border-radius: 18px;
            padding: 1.1rem;
        }

        .app-title {
            color: #f8fafc;
            font-size: 2.2rem;
            font-weight: 700;
            margin-bottom: 0.2rem;
        }

        .app-subtitle {
            color: #94a3b8;
            font-size: 0.9rem;
            margin-bottom: 1.4rem;
        }

        .section-title {
            color: #f59e0b;
            font-size: 1.2rem;
            font-weight: 700;
            margin-bottom: 1rem;
        }

        .bond-name {
            color: #ffffff;
            font-size: 1.3rem;
            font-weight: 700;
            margin-top: 1rem;
            margin-bottom: 0.3rem;
        }

        .bond-meta {
            color: #9ca3af;
            font-size: 0.85rem;
            margin-bottom: 0.2rem;
        }

        .metric-box {
            background-color: #0f172a;
            border: 1px solid #334155;
            border-radius: 14px;
            padding: 1rem;
            margin-bottom: 0.8rem;
        }

        .metric-label {
            color: #94a3b8;
            font-size: 0.8rem;
            margin-bottom: 0.35rem;
        }

        .metric-value {
            color: #f8fafc;
            font-size: 1.6rem;
            font-weight: 700;
        }

        div[data-testid="stDataFrame"] {
            border: 1px solid #334155;
            border-radius: 12px;
            overflow: hidden;
        }

        div[data-testid="stTextInput"] label,
        div[data-testid="stNumberInput"] label,
        div[data-testid="stDateInput"] label,
        div[data-testid="stSelectbox"] label {
            color: #cbd5e1 !important;
        }

        div[data-testid="stAlert"] {
            border-radius: 12px;
        }

        .market-title {
            color: #94a3b8;
            font-size: 0.75rem;
            font-weight: 700;
            margin-bottom: 0.7rem;
            letter-spacing: 0.04rem;
        }

        .market-card {
            background-color: #0f172a;
            border: 1px solid #334155;
            border-radius: 10px;
            padding: 0.6rem;
            min-height: 110px;
        }

        .market-card-label {
            color: #94a3b8;
            font-size: 0.72rem;
            margin-bottom: 0.25rem;
        }

        .market-card-value {
            color: #f8fafc;
            font-size: 1.1rem;
            font-weight: 700;
        }

        .market-card-spread {
            color: #f59e0b;
            font-size: 0.78rem;
            margin-top: 0.35rem;
        }

        .market-card-reference {
            color: #94a3b8;
            font-size: 0.78rem;
            margin-top: 0.35rem;
        }

        @media (max-width: 1200px) {
            .market-grid {
                grid-template-columns: repeat(4, 1fr);
            }
        }

        @media (max-width: 800px) {
            .market-grid {
                grid-template-columns: repeat(2, 1fr);
            }
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# 5. CALCUL DES SPREADS CONTRE LE BUND
# ============================================================

def calculate_spreads(rates):
    """
    Calcule les spreads des obligations européennes contre le Bund.

    Formule :
        Spread = taux du pays - taux du Bund

    Conversion :
        1 % = 100 points de base
    """

    bund_rate = None

    # Recherche du taux Bund.
    for rate in rates:
        if rate["label"] == "Bund 10Y":
            bund_rate = rate["value"]
            break

    result = []

    for rate in rates:

        current_rate = rate["value"]

        # Le spread ne peut pas être calculé sans taux Bund.
        if (
            bund_rate is None
            or current_rate is None
            or rate["region"] not in ["Europe"]
        ):
            spread = None

        else:
            spread = (
                current_rate - bund_rate
            ) * 100

        result.append(
            {
                "label": rate["label"],
                "value": current_rate,
                "region": rate["region"],
                "spread": spread,
            }
        )

    return result


# ============================================================
# 6. AFFICHAGE DU BANDEAU DE MARCHÉ
# ============================================================

def render_market_banner(rates):
    """
    Affiche les taux et spreads dans des cartes Streamlit.

    - US 10Y : taux uniquement
    - Bund 10Y : taux + référence
    - Autres pays européens : taux + spread contre Bund
    """

    st.markdown(
        '<div class="market-title">'
        "10Y GOVERNMENT BOND RATES & SPREADS"
        "</div>",
        unsafe_allow_html=True,
    )

    columns = st.columns(
        len(rates),
        gap="small",
    )

    for column, rate in zip(columns, rates):

        with column:

            with st.container(border=True):

                st.markdown(
                    f"""
                    <div class="market-card">
                        <div class="market-card-label">
                            {html.escape(rate["label"])}
                        </div>

                        <div class="market-card-value">
                            {
                                "N/A"
                                if rate["value"] is None
                                else f"{rate["value"]:.2f}%"
                            }
                        </div>

                        {
                            '<div class="market-card-reference">'
                            'Reference'
                            '</div>'
                            if rate["label"] == "Bund 10Y"
                            else (
                                '<div class="market-card-spread">'
                                f"Spread: "
                                f"{rate['spread']:+.1f} bp"
                                "</div>"
                                if rate["spread"] is not None
                                else '<div class="market-card-reference">'
                                "Spread unavailable"
                                "</div>"
                            )
                        }
                    </div>
                    """,
                    unsafe_allow_html=True,
                )


# ============================================================
# 7. GÉNÉRATION DES CASH FLOWS
# ============================================================

def generate_cashflows(
    face_value,
    coupon_rate,
    issue_date,
    maturity_date,
    frequency,
):
    """
    Génère les coupons et le remboursement du nominal.
    """

    today = pd.Timestamp.today().normalize()

    issue_timestamp = pd.Timestamp(issue_date)
    maturity_timestamp = pd.Timestamp(maturity_date)

    if maturity_timestamp <= issue_timestamp:
        return pd.DataFrame(
            columns=["Date", "Cash Flow", "Status"]
        )

    coupon_amount = (
        face_value * coupon_rate / frequency
    )

    months_between_payments = 12 // frequency

    payment_dates = []

    current_date = issue_timestamp + pd.DateOffset(
        months=months_between_payments
    )

    while current_date < maturity_timestamp:

        payment_dates.append(current_date)

        current_date += pd.DateOffset(
            months=months_between_payments
        )

    payment_dates.append(maturity_timestamp)

    rows = []

    for payment_date in payment_dates:

        cashflow_amount = coupon_amount

        if payment_date == maturity_timestamp:
            cashflow_amount += face_value

        status = (
            "Past"
            if payment_date < today
            else "Future"
        )

        rows.append(
            {
                "Date": payment_date,
                "Cash Flow": round(cashflow_amount, 2),
                "Status": status,
            }
        )

    return pd.DataFrame(rows)


# ============================================================
# 8. CALCUL DES MÉTRIQUES
# ============================================================

def compute_bond_metrics(
    face_value,
    coupon_rate,
    ytm,
    issue_date,
    maturity_date,
    frequency,
):
    """
    Calcule Duration, Modified Duration et DV01.
    """

    today = pd.Timestamp.today().normalize()

    cashflows = generate_cashflows(
        face_value=face_value,
        coupon_rate=coupon_rate,
        issue_date=issue_date,
        maturity_date=maturity_date,
        frequency=frequency,
    )

    future_cashflows = cashflows[
        cashflows["Date"] >= today
    ].copy()

    if future_cashflows.empty:
        return {
            "duration": 0.0,
            "modified_duration": 0.0,
            "dv01": 0.0,
            "cashflows": cashflows,
        }

    future_cashflows["Time"] = (
        future_cashflows["Date"] - today
    ).dt.days / 365.25

    periodic_yield = ytm / frequency

    future_cashflows["Discount Factor"] = 1 / (
        (1 + periodic_yield)
        ** (future_cashflows["Time"] * frequency)
    )

    future_cashflows["Present Value"] = (
        future_cashflows["Cash Flow"]
        * future_cashflows["Discount Factor"]
    )

    bond_price = future_cashflows["Present Value"].sum()

    if bond_price <= 0:
        return {
            "duration": 0.0,
            "modified_duration": 0.0,
            "dv01": 0.0,
            "cashflows": cashflows,
        }

    duration = (
        future_cashflows["Time"]
        * future_cashflows["Present Value"]
    ).sum() / bond_price

    modified_duration = (
        duration / (1 + periodic_yield)
    )

    dv01 = (
        modified_duration
        * bond_price
        * 0.0001
    )

    return {
        "duration": duration,
        "modified_duration": modified_duration,
        "dv01": dv01,
        "cashflows": cashflows,
    }


# ============================================================
# 9. STYLE DU TABLEAU
# ============================================================

def style_cashflow_rows(row):
    """
    Grise les flux passés et conserve les flux futurs en clair.
    """

    if row["Status"] == "Past":
        return [
            "background-color: #111827; color: #6b7280;"
            for _ in row
        ]

    return [
        "background-color: #0f172a; color: #f8fafc;"
        for _ in row
    ]


# ============================================================
# 10. CARTES DE RISQUE
# ============================================================

def render_metric_box(label, value):
    """
    Génère une carte HTML pour une métrique.
    """

    return f"""
    <div class="metric-box">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
    </div>
    """


# ============================================================
# 11. TITRE ET BANDEAU
# ============================================================

st.markdown(
    '<div class="app-title">📈 Bond Analyzer</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="app-subtitle">'
    "Single-page Streamlit project for bond analytics"
    "</div>",
    unsafe_allow_html=True,
)

market_data = calculate_spreads(
    MANUAL_MARKET_RATES
)

render_market_banner(market_data)


# ============================================================
# 12. CARTE BOND INPUT
# ============================================================

with st.container(border=True):

    st.markdown(
        '<div class="section-title">Bond Input</div>',
        unsafe_allow_html=True,
    )

    # Ligne 1 : identification
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

    # Ligne 2 : paramètres financiers
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
            min_value=0.0,
            value=0.0,
            step=0.1,
        )

    # Ligne 3 : calendrier
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

    # Résumé de l'obligation
    st.markdown(
        f"""
        <div class="bond-name">
            {html.escape(bond_name) if bond_name else "-"}
        </div>

        <div class="bond-meta">
            ISIN: {html.escape(isin) if isin else "-"}
            |
            Issuer: {html.escape(issuer) if issuer else "-"}
            |
            Coupon: {coupon:.2f}%
            |
            Yield: {ytm:.2f}%
        </div>

        <div class="bond-meta">
            Issue Date: {issue_date}
            |
            Maturity: {maturity_date}
            |
            Face Value: {face_value:,.2f}
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# 13. VALIDATION DES INPUTS
# ============================================================

valid_dates = maturity_date > issue_date
valid_face_value = face_value > 0
valid_coupon = coupon > 0
valid_ytm = ytm > 0

inputs_are_valid = (
    valid_dates
    and valid_face_value
    and valid_coupon
    and valid_ytm
)


# ============================================================
# 14. AFFICHAGE CONDITIONNEL DES CARTES
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

    analytics = compute_bond_metrics(
        face_value=face_value,
        coupon_rate=coupon / 100,
        ytm=ytm / 100,
        issue_date=issue_date,
        maturity_date=maturity_date,
        frequency=frequency,
    )

    cashflows = analytics["cashflows"]

    risk_column, cashflow_column = st.columns(
        [1, 2],
        gap="large",
    )

    # --------------------------------------------------------
    # Risk Metrics
    # --------------------------------------------------------

    with risk_column:

        with st.container(border=True):

            st.markdown(
                '<div class="section-title">'
                "Risk Metrics"
                "</div>",
                unsafe_allow_html=True,
            )

            st.markdown(
                render_metric_box(
                    "Duration",
                    f"{analytics['duration']:.2f}",
                ),
                unsafe_allow_html=True,
            )

            st.markdown(
                render_metric_box(
                    "Modified Duration",
                    f"{analytics['modified_duration']:.2f}",
                ),
                unsafe_allow_html=True,
            )

            st.markdown(
                render_metric_box(
                    "DV01",
                    f"{analytics['dv01']:.4f}",
                ),
                unsafe_allow_html=True,
            )

    # --------------------------------------------------------
    # Cash Flow Schedule
    # --------------------------------------------------------

    with cashflow_column:

        with st.container(border=True):

            st.markdown(
                '<div class="section-title">'
                "Cash Flow Schedule"
                "</div>",
                unsafe_allow_html=True,
            )

            if cashflows.empty:

                st.info(
                    "No cash flows available for this bond."
                )

            else:

                display_cashflows = cashflows.copy()

                display_cashflows["Date"] = (
                    pd.to_datetime(
                        display_cashflows["Date"]
                    ).dt.strftime("%Y-%m-%d")
                )

                styled_cashflows = (
                    display_cashflows.style
                    .apply(
                        style_cashflow_rows,
                        axis=1,
                    )
                    .format(
                        {
                            "Cash Flow": "{:,.2f}",
                        }
                    )
                )

                st.dataframe(
                    styled_cashflows,
                    hide_index=True,
                    use_container_width=True,
                    height=250,
                )
