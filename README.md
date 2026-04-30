```markdown
# Financial Engineering & Quantitative Analysis Portfolio

This repository serves as an interactive portfolio showcasing quantitative finance tools and credit risk models. The goal is to bridge the gap between academic financial theory and functional, data-driven applications.

**Live Demo:** https://financeboard-anthonym.streamlit.app

---

## 🛠 Project Modules

### 1. Credit Risk & Corporate Scoring
*   **Core Model:** Implementation of the **Altman Z-Score** to predict the probability of bankruptcy.
*   **Automation:** Real-time extraction of financial statements (Balance Sheet, Income Statement) using the Yahoo Finance API.
*   **Key Metrics:** Solvency, Liquidity, and Profitability ratios analysis with sector-based benchmarking.

### 2. Strategy Backtesting (Sales & Trading)
*   **Engine:** Quantitative analysis of historical price data to evaluate trading strategies.
*   **Risk Metrics:** Calculation of **Sharpe Ratio**, **Maximum Drawdown**, and **Annualized Volatility**.
*   **Visualization:** Interactive equity curves and performance heatmaps.

### 3. Derivatives Pricing (Capital Markets)
*   **Models:** Black-Scholes-Merton formula for European options.
*   **The Greeks:** Sensitivity analysis (Delta, Gamma, Vega, Theta).
*   **Simulation:** Monte Carlo methods for path-dependent asset pricing.

---

## 💻 Tech Stack

*   **Language:** Python 3.x
*   **Data Science:** `Pandas`, `NumPy`, `SciPy`
*   **Financial Data:** `yFinance` (Yahoo Finance API)
*   **Visualization:** `Plotly`, `Matplotlib`
*   **Deployment:** `Streamlit`

---

## 📂 Project Structure

```text
├── app.py                # Main landing page (Portfolio Hub)
├── requirements.txt      # Project dependencies
├── .gitignore            # Python cache and environment exclusion
└── pages/                # Multi-page application structure
    ├── 01_Credit_Risk.py
    ├── 02_Backtesting.py
    └── 03_Option_Pricing.py
