# ============================================================
# BOND ANALYZER
# ============================================================

import html
from datetime import date, timedelta

import pandas as pd
import streamlit as st


# ============================================================
# 1. CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Bond Analyzer",
    page_icon="📈",
    layout="wide",
)


# ============================================================
# 2. STYLE CSS
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
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# 3. CALCUL DES CASH FLOWS
# ============================================================

def generate_cashflows(
    face_value: float,
    coupon_rate: float,
    issue_date: date,
    maturity_date: date,
    frequency: int,
) -> pd.DataFrame:
    """
    Génère les flux de coupons et le remboursement final du nominal.
    """

    today = pd.Timestamp.today().normalize()

    issue_timestamp = pd.Timestamp(issue_date)
    maturity_timestamp = pd.Timestamp(maturity_date)

    # Si les dates sont incohérentes, on retourne un tableau vide.
    if maturity_timestamp <= issue_timestamp:
        return pd.DataFrame(
            columns=["Date", "Cash Flow", "Status"]
        )

    # Montant d'un coupon.
    coupon_amount = face_value * coupon_rate / frequency

    # Nombre de mois entre deux paiements.
    months_between_payments = 12 // frequency

    payment_dates = []

    # Premier coupon après la date d'émission.
    current_date = issue_timestamp + pd.DateOffset(
        months=months_between_payments
    )

    # Ajout des coupons intermédiaires.
    while current_date < maturity_timestamp:
        payment_dates.append(current_date)

        current_date += pd.DateOffset(
            months=months_between_payments
        )

    # La maturité est toujours ajoutée comme dernière date.
    payment_dates.append(maturity_timestamp)

    rows = []

    for payment_date in payment_dates:
        cashflow_amount = coupon_amount

        # À la maturité, on rembourse aussi le nominal.
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
# 4. CALCUL DES MÉTRIQUES
# ============================================================

def compute_bond_metrics(
    face_value: float,
    coupon_rate: float,
    ytm: float,
    issue_date: date,
    maturity_date: date,
    frequency: int,
) -> dict:
    """
    Calcule :
    - Duration
    - Modified Duration
    - DV01
    """

    today = pd.Timestamp.today().normalize()

    cashflows = generate_cashflows(
        face_value=face_value,
        coupon_rate=coupon_rate,
        issue_date=issue_date,
        maturity_date=maturity_date,
        frequency=frequency,
    )

    # Seuls les flux futurs servent au calcul des risques.
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

    # Temps restant avant chaque paiement, en années.
    future_cashflows["Time"] = (
        future_cashflows["Date"] - today
    ).dt.days / 365.25

    # Yield par période.
    periodic_yield = ytm / frequency

    # Actualisation des flux.
    future_cashflows["Discount Factor"] = 1 / (
        (1 + periodic_yield)
        ** (future_cashflows["Time"] * frequency)
    )

    # Valeur présente de chaque flux.
    future_cashflows["Present Value"] = (
        future_cashflows["Cash Flow"]
        * future_cashflows["Discount Factor"]
    )

    # Prix théorique.
    bond_price = future_cashflows["Present Value"].sum()

    if bond_price <= 0:
        return {
            "duration": 0.0,
            "modified_duration": 0.0,
            "dv01": 0.0,
            "cashflows": cashflows,
        }

    # Duration de Macaulay.
    duration = (
        future_cashflows["Time"]
        * future_cashflows["Present Value"]
    ).sum() / bond_price

    # Duration modifiée.
    modified_duration = duration / (1 + periodic_yield)

    # Approximation du DV01.
    dv01 = modified_duration * bond_price * 0.0001

    return {
        "duration": duration,
        "modified_duration": modified_duration,
        "dv01": dv01,
        "cashflows": cashflows,
    }


# ============================================================
# 5. STYLE DU TABLEAU
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
# 6. AFFICHAGE DES MÉTRIQUES
# ============================================================

def render_metric_box(label: str, value: str) -> str:
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
# 7. TITRE
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


# ============================================================
# 8. CARTE BOND INPUT
# ============================================================

with st.container(border=True):

    st.markdown(
        '<div class="section-title">Bond Input</div>',
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # Ligne 1 : identification
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Ligne 2 : paramètres financiers
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Ligne 3 : dates et fréquence
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Résumé de l'obligation
    # --------------------------------------------------------

    safe_bond_name = (
        html.escape(bond_name.strip())
        if bond_name.strip()
        else "-"
    )

    safe_isin = (
        html.escape(isin.strip())
        if isin.strip()
        else "-"
    )

    safe_issuer = (
        html.escape(issuer.strip())
        if issuer.strip()
        else "-"
    )

    st.markdown(
        f"""
        <div class="bond-name">
            {safe_bond_name}
        </div>

        <div class="bond-meta">
            ISIN: {safe_isin}
            |
            Issuer: {safe_issuer}
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
# 9. VALIDATION DES INPUTS
# ============================================================

# Les cartes d'analyse ne s'afficheront que si ces conditions sont vraies.
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
# 10. AFFICHAGE CONDITIONNEL
# ============================================================

if not inputs_are_valid:

    # On indique à l'utilisateur ce qui manque.
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

    # ========================================================
    # 11. CALCUL DES ANALYTICS
    # ========================================================

    analytics = compute_bond_metrics(
        face_value=face_value,
        coupon_rate=coupon / 100,
        ytm=ytm / 100,
        issue_date=issue_date,
        maturity_date=maturity_date,
        frequency=frequency,
    )

    cashflows = analytics["cashflows"]

    # ========================================================
    # 12. CARTES D'ANALYSE
    # ========================================================

    risk_column, cashflow_column = st.columns(
        [1, 2],
        gap="large",
    )

    # --------------------------------------------------------
    # Carte Risk Metrics
    # --------------------------------------------------------

    with risk_column:

        with st.container(border=True):

            st.markdown(
                '<div class="section-title">Risk Metrics</div>',
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
    # Carte Cash Flow Schedule
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

                # Copie utilisée uniquement pour l'affichage.
                display_cashflows = cashflows.copy()

                # Format lisible des dates.
                display_cashflows["Date"] = (
                    pd.to_datetime(display_cashflows["Date"])
                    .dt.strftime("%Y-%m-%d")
                )

                # Style du tableau.
                styled_cashflows = (
                    display_cashflows.style
                    .apply(style_cashflow_rows, axis=1)
                    .format(
                        {
                            "Cash Flow": "{:,.2f}",
                        }
                    )
                )

                # Hauteur limitée à environ cinq lignes.
                # Les autres lignes sont accessibles par défilement.
                st.dataframe(
                    styled_cashflows,
                    hide_index=True,
                    use_container_width=True,
                    height=250,
                )
