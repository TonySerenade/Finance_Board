import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(
    page_title="Bond Analyzer",
    page_icon="📈",
    layout="wide"
)

# ---------------------------------------------------
# CALCULS OBLIGATAIRES
# ---------------------------------------------------
def generate_cashflows(face_value, coupon_rate, maturity_date, frequency=1):
    today = pd.Timestamp.today().normalize()

    if maturity_date <= today:
        return pd.DataFrame(columns=["date", "cashflow", "status"])

    coupon_amount = face_value * coupon_rate / frequency

    months_step = int(12 / frequency)
    dates = []
    current_date = maturity_date

    while current_date > today:
        dates.append(current_date)
        current_date = current_date - pd.DateOffset(months=months_step)

    dates = sorted(dates)

    cashflows = []
    for i, d in enumerate(dates):
        amount = coupon_amount
        if i == len(dates) - 1:
            amount += face_value

        cashflows.append({
            "date": d,
            "cashflow": round(amount, 2),
            "status": "Past" if d < today else "Future"
        })

    return pd.DataFrame(cashflows)


def compute_bond_metrics(face_value, coupon_rate, ytm, maturity_date, frequency=1):
    today = pd.Timestamp.today().normalize()
    cashflows_df = generate_cashflows(face_value, coupon_rate, maturity_date, frequency)

    if cashflows_df.empty:
        return {
            "duration": 0.0,
            "modified_duration": 0.0,
            "dv01": 0.0,
            "cashflows": cashflows_df
        }

    future_cf = cashflows_df[cashflows_df["date"] >= today].copy()

    future_cf["t"] = (future_cf["date"] - today).dt.days / 365.25
    period_rate = ytm / frequency
    future_cf["discount_factor"] = 1 / ((1 + period_rate) ** (future_cf["t"] * frequency))
    future_cf["pv"] = future_cf["cashflow"] * future_cf["discount_factor"]

    price = future_cf["pv"].sum()

    if price == 0:
        duration = 0.0
        modified_duration = 0.0
        dv01 = 0.0
    else:
        duration = (future_cf["t"] * future_cf["pv"]).sum() / price
        modified_duration = duration / (1 + period_rate)
        dv01 = modified_duration * price * 0.0001

    return {
        "duration": round(duration, 4),
        "modified_duration": round(modified_duration, 4),
        "dv01": round(dv01, 4),
        "cashflows": cashflows_df
    }


# ---------------------------------------------------
# STYLE
# ---------------------------------------------------
st.markdown("""
<style>
    .stApp {
        background-color: #0b0f14;
        color: #e6e6e6;
    }

    .main-card {
        background-color: #111827;
        border: 1px solid #2d3748;
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
    }

    .sub-card {
        background-color: #111827;
        border: 1px solid #2d3748;
        border-radius: 16px;
        padding: 20px;
        min-height: 420px;
    }

    .section-title {
        color: #f59e0b;
        font-size: 22px;
        font-weight: 700;
        margin-bottom: 12px;
    }

    .bond-title {
        color: #ffffff;
        font-size: 24px;
        font-weight: 700;
        margin-bottom: 6px;
    }

    .bond-subtitle {
        color: #9ca3af;
        font-size: 14px;
        margin-bottom: 18px;
    }

    .metric-box {
        background-color: #0f172a;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 14px;
        margin-bottom: 12px;
    }

    .metric-label {
        color: #94a3b8;
        font-size: 13px;
        margin-bottom: 4px;
    }

    .metric-value {
        color: #f8fafc;
        font-size: 26px;
        font-weight: 700;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------
# HEADER
# ---------------------------------------------------
st.title("📈 Bond Analyzer")
st.caption("Single-page Streamlit project for bond analytics")

# ---------------------------------------------------
# TOP CARD : USER INPUT
# ---------------------------------------------------
st.markdown('<div class="main-card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">Bond Input</div>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    isin = st.text_input("ISIN", placeholder="Ex: FR001400FYQ4")
    issuer = st.text_input("Issuer", placeholder="Ex: France")

with col2:
    bond_name = st.text_input("Bond Name", placeholder="Ex: OAT 2.50% 25-May-2030")
    face_value = st.number_input("Face Value", min_value=0.0, value=100.0, step=100.0)

with col3:
    coupon = st.number_input("Coupon (%)", min_value=0.0, value=2.5, step=0.1)
    ytm = st.number_input("Yield (%)", min_value=0.0, value=2.3, step=0.1)

with col4:
    maturity = st.date_input("Maturity Date", value=datetime(2030, 5, 25))
    frequency = st.selectbox("Coupon Frequency", options=[1, 2], format_func=lambda x: "Annual" if x == 1 else "Semi-Annual")

st.markdown(f"""
<div class="bond-title">{bond_name if bond_name else "No bond selected yet"}</div>
<div class="bond-subtitle">
ISIN: {isin if isin else "-"} | Issuer: {issuer if issuer else "-"} | Coupon: {coupon:.2f}% | Yield: {ytm:.2f}%
</div>
""", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------
# CALCUL DES METRICS
# ---------------------------------------------------
metrics = compute_bond_metrics(
    face_value=face_value,
    coupon_rate=coupon / 100,
    ytm=ytm / 100,
    maturity_date=pd.Timestamp(maturity),
    frequency=frequency
)

left_col, right_col = st.columns([1, 2])

# ---------------------------------------------------
# LEFT CARD : RISK METRICS
# ---------------------------------------------------
with left_col:
    st.markdown('<div class="sub-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Risk Metrics</div>', unsafe_allow_html=True)

    st.markdown(f"""
    <div class="metric-box">
        <div class="metric-label">Duration</div>
        <div class="metric-value">{metrics["duration"]:.2f}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="metric-box">
        <div class="metric-label">Modified Duration</div>
        <div class="metric-value">{metrics["modified_duration"]:.2f}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="metric-box">
        <div class="metric-label">DV01</div>
        <div class="metric-value">{metrics["dv01"]:.4f}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------
# RIGHT CARD : CASH FLOW SCHEDULE
# ---------------------------------------------------
with right_col:
    st.markdown('<div class="sub-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Cash Flow Schedule</div>', unsafe_allow_html=True)

    cf_df = metrics["cashflows"].copy()

    if cf_df.empty:
        st.warning("No future cash flows available for this bond.")
    else:
        cf_df["date"] = pd.to_datetime(cf_df["date"]).dt.date

        def highlight_past_rows(row):
            if row["status"] == "Past":
                return ["color: gray; opacity: 0.6;"] * len(row)
            return [""] * len(row)

        styled_cf = cf_df.style.apply(highlight_past_rows, axis=1)

        st.dataframe(
            styled_cf,
            use_container_width=True,
            hide_index=True
        )

    st.markdown("</div>", unsafe_allow_html=True)
