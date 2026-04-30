import streamlit as st

# Global page configuration
st.set_page_config(
    page_title="Quant Finance Portfolio",
    page_icon="⚖️",
    layout="wide"
)

# --- SIDEBAR (Optional) ---
with st.sidebar:
    st.markdown("### Contact Details")
    st.write("📫 [Your Email]")
    st.write("🔗 [Your LinkedIn Profile]")
    st.write("💻 [GitHub Repository]")

# --- HERO SECTION ---
st.title("📈 Quantitative Finance & Risk Analysis")
st.subheader("Bridging Financial Theory and Data Engineering")

st.markdown("""
Welcome! This platform is a curated collection of financial models and interactive tools. 
It reflects my journey in exploring market mechanics and credit risk through code.
""")

st.divider()

# --- ABOUT ME SECTION ---
col_about, col_img = st.columns([2, 1])

with col_about:
    st.header("🔍 Why This Portfolio?")
    st.markdown("""
    I've always believed that finance is best understood when you can **build and break the models yourself**. 
    For me, it's not just about reading formulas in a textbook; it's about seeing how they react to real-time market shifts.
    
    **What drives me:**
    *   **The "Why" behind the numbers:** I enjoy deep-diving into research papers (like Altman's or Black-Scholes) and translating them into functional code.
    *   **Data Integrity:** Building tools that fetch live data proves that a model is only as good as the pipeline feeding it.
    *   **User Experience:** Finance can be complex. I aim to create interfaces that make quantitative analysis accessible and visually intuitive.
    
    Currently, I am focusing on **Quantitative Research** and **Risk Management**, looking for ways to optimize decision-making through automation.
    """)

with col_img:
    # A nice info box or you can even put a placeholder for a photo
    st.info("""
    **Core Philosophy:**
    > "In God we trust, all others must bring data." 
    > — *W. Edwards Deming*
    """)

st.divider()

# --- PROJECT SHOWCASE ---
st.header("🚀 Interactive Modules")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🏦 Corporate Credit Risk")
    st.markdown("""
    Evaluates company solvency using the **Altman Z-Score**. This tool fetches live Balance Sheets 
    and Income Statements to predict financial distress.
    """)
    if st.button("Launch Credit Risk Tool"):
        st.switch_page("pages/01_Analyse_Credit.py") # Make sure the filename matches exactly

with col2:
    st.markdown("### 🧮 Option Pricing & Greeks")
    st.markdown("""
    A **Black-Scholes-Merton** implementation to price European options. 
    It calculates real-time sensitivity metrics (Delta, Gamma, Vega, Theta) with interactive visualizations.
    """)
    if st.button("Launch Option Pricing Tool"):
        st.switch_page("pages/02_Option_Pricing.py") # Make sure the filename matches exactly

st.divider()

# --- TECHNICAL TOOLKIT ---
st.header("🛠 Technical Toolkit")
c1, c2, c3 = st.columns(3)

with c1:
    st.write("**Finance & Math**")
    st.caption("Quantitative Research, Options Greeks, Credit Scoring, Probability Distributions.")

with c2:
    st.write("**Data Stack**")
    st.caption("Python (Pandas, NumPy, SciPy), Requests (REST APIs), YFinance.")

with c3:
    st.write("**Visualization**")
    st.caption("Streamlit Framework, Plotly Interactive Charts, LaTeX.")

# --- FOOTER ---
st.divider()
st.caption("© 2026 - Quantitative Portfolio | Built with passion for Financial Markets.")
