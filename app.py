import streamlit as st

# Configuration globale de la page
st.set_page_config(
    page_title="Quant Finance Portfolio",
    page_icon="⚖️",
    layout="wide"
)

# --- SIDEBAR (Navigation par défaut de Streamlit) ---
with st.sidebar:
    st.markdown("### Navigation")
    st.write("Use the interactive buttons on the main page to explore the modules.")

# --- HERO SECTION ---
st.title("📈 Quantitative Finance & Risk Analysis")
st.subheader("Bridging Financial Theory and Data Engineering")

st.markdown("""
Welcome! This platform is a curated collection of financial models and interactive tools. 
It reflects my journey in exploring market mechanics, credit risk, and real-time intelligence through code.
""")

st.divider()

# --- PROJECT SHOWCASE ---
st.header("🚀 Interactive Modules")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 🏦 Corporate Credit Risk")
    st.markdown("""
    Evaluates company solvency using the **Altman Z-Score**. Fetches live financial statements 
    to predict potential distress.
    """)
    if st.button("Launch Credit Tool", use_container_width=True):
        st.switch_page("pages/01_Credit_risk_:_Z-score.py")

with col2:
    st.markdown("### 🧮 Option Pricing")
    st.markdown("""
    A **Black-Scholes-Merton** implementation to price European options. 
    Calculates Greeks and visualizes sensitivities.
    """)
    if st.button("Launch Pricing Tool", use_container_width=True):
        st.switch_page("pages/02_Option_Pricing.py")

with col3:
    st.markdown("### 🗞️ Market Intelligence")
    st.markdown("""
    Real-time terminal for **fundamental analysis**. Aggregates news, corporate agendas, 
    and key valuation metrics.
    """)
    if st.button("Launch Intel Tool", use_container_width=True):
        st.switch_page("pages/03_Market_Intelligence.py")

st.divider()

# --- ABOUT ME SECTION ---
st.header("🔍 Why This Portfolio?")
st.markdown("""
I've always believed that finance is best understood when you can **build and break the models yourself**. 
For me, it's not just about reading formulas; it's about seeing how they react to real-time market shifts.

**What drives me:**
*   **The "Why" behind the numbers:** Translating research papers into functional, automated code.
*   **Data Integrity:** Building robust pipelines to ensure models are fed with high-quality live data.
*   **User Experience:** Creating intuitive interfaces to make complex quantitative analysis accessible.

Currently focusing on **Quantitative Research** and **Risk Management**, leveraging AI to optimize development and decision-making.
""")

st.divider()

# --- TECHNICAL TOOLKIT ---
st.header("🛠 Technical Toolkit")
c1, c2, c3, c4 = st.columns(4)

with c1:
    st.write("**Finance & Math**")
    st.caption("Quant Research, Options Greeks, Credit Scoring, Probability.")

with c2:
    st.write("**Data Stack**")
    st.caption("Python (Pandas, NumPy, SciPy), REST APIs, YFinance.")

with c3:
    st.write("**Visualization**")
    st.caption("Streamlit, Plotly Interactive Charts, LaTeX.")

with c4:
    st.write("**AI Engineering**")
    st.caption("LLMs for code optimization, debugging, and rapid prototyping.")

# --- CONTACT SECTION ---
st.divider()
st.subheader("📬 Contact & Networking")
st_col1, st_col2, st_col3 = st.columns(3)

with st_col1:
    st.markdown("🔗 [LinkedIn Profile](https://www.linkedin.com/in/anthony-moubarak-1771a7251/)")
with st_col2:
    st.markdown("💻 [GitHub Repository](https://github.com/TonySerenade/Finance_Board)")
with st_col3:
    st.markdown(f"📫 [anthony.moubarak14@gmail.com](mailto:anthony.moubarak14@gmail.com)")

st.caption("<br><center>© 2026 - Finance Board | Built with Passion</center>", unsafe_allow_html=True)
