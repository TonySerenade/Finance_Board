import streamlit as st

st.set_page_config(
    page_title="Finance Portfolio | Analysis & Risk",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Quantitative Finance & Risk Portfolio")
st.markdown("""
Welcome to my financial analysis dashboard. This project demonstrates the application of 
quantitative models to real-world financial data.

### 👈 Select a tool from the sidebar to begin
---
""")

# Présentation des sections
col1, col2 = st.columns(2)

with col1:
    st.info("### 🏦 Credit Risk Analysis")
    st.write("Using the **Altman Z-Score** to evaluate corporate solvency and bankruptcy risk.")

with col2:
    st.success("### 📈 Market Strategies")
    st.write("Backtesting and performance metrics for trading strategies (Coming soon).")
