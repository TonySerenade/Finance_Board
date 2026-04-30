import streamlit as st
import numpy as np
from scipy.stats import norm
import pandas as pd
import plotly.graph_objects as go

# Page configuration for a professional wide layout
st.set_page_config(page_title="Option Pricing Model", layout="wide")

# --- MATHEMATICAL FUNCTIONS (Black-Scholes Model) ---

def black_scholes(S, K, T, r, sigma, option_type="call"):
    """
    S : Current Stock Price (Spot)
    K : Strike Price
    T : Time to Maturity in years
    r : Risk-free interest rate
    sigma : Implied Volatility
    """
    
    # Step 1: Calculate d1 and d2 (probability variables)
    # d1 represents the probability of the option finishing in-the-money (ITM)
    d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    # d2 is used to determine the present value of the strike price to be paid
    d2 = d1 - sigma * np.sqrt(T)
    
    # Step 2: Calculate Option Price based on type
    if option_type == "call":
        # Call Formula: S*N(d1) - K*exp(-rt)*N(d2)
        price = S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
        # Call Delta: Sensitivity of the option price to a change in the spot price
        delta = norm.cdf(d1)
    else:
        # Put Formula: K*exp(-rt)*N(-d2) - S*N(-d1)
        price = K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
        # Put Delta: Always between -1 and 0
        delta = norm.cdf(d1) - 1
        
    # Step 3: Calculate "The Greeks" (Risk Management Indicators)
    
    # Gamma (Γ): Sensitivity of the Delta relative to changes in the spot price
    gamma = norm.pdf(d1) / (S * sigma * np.sqrt(T))
    
    # Vega (ν): Sensitivity of the option price relative to implied volatility
    vega = S * norm.pdf(d1) * np.sqrt(T)
    
    # Theta (θ): Time decay (Value lost for each passing day)
    theta = -(S * norm.pdf(d1) * sigma) / (2 * np.sqrt(T)) - r * K * np.exp(-r * T) * norm.cdf(d2 if option_type=="call" else -d2)
    
    return price, delta, gamma, vega, theta

# --- STREAMLIT USER INTERFACE ---

st.title("🧮 Option Pricing & Greeks (Black-Scholes)")

# Theoretical section for the recruiter
with st.expander("📖 Theoretical Context"):
    st.write("""
    The Black-Scholes-Merton model (1973) is the industry standard for valuing European options. 
    It assumes that stock prices follow a geometric Brownian motion with constant volatility.
    """)
    st.latex(r"C = S_t N(d_1) - K e^{-rt} N(d_2)")

st.divider()

# Create 3 columns for input parameters
col_in1, col_in2, col_in3 = st.columns(3)

with col_in1:
    st.markdown("**Market Parameters**")
    S = st.number_input("Underlying Asset Price (S)", value=100.0, help="Current market price of the stock")
    K = st.number_input("Strike Price (K)", value=100.0, help="Price at which you can buy/sell the asset")

with col_in2:
    st.markdown("**Time Parameters**")
    T = st.slider("Time to Maturity (Years)", 0.01, 2.0, 0.5, help="Time remaining until option expiration")
    r = st.slider("Risk-Free Rate (%)", 0.0, 10.0, 2.0) / 100

with col_in3:
    st.markdown("**Risk & Type**")
    sigma = st.slider("Volatility (σ) (%)", 1.0, 100.0, 20.0) / 100
    opt_type = st.selectbox("Option Type", ["Call", "Put"]).lower()

# Execute financial calculation
price, delta, gamma, vega, theta = black_scholes(S, K, T, r, sigma, opt_type)

# --- RESULTS DISPLAY ---

st.subheader(f"Theoretical Option Price: ${price:.2f}")

# Display Risk Metrics (Greeks) in visual containers
m1, m2, m3, m4 = st.columns(4)
m1.metric("Delta (Δ)", f"{delta:.3f}", help="Sensitivity to price. If S increases by $1, the option price changes by Delta.")
m2.metric("Gamma (Γ)", f"{gamma:.4f}", help="Delta stability. Crucial for Delta Hedging strategies.")
m3.metric("Vega (ν)", f"{vega:.3f}", help="Volatility sensitivity. Impact of a 1% increase in sigma.")
m4.metric("Theta (θ)", f"{theta:.3f}", help="Time decay impact (daily value loss).")

st.divider()

# --- SENSITIVITY VISUALIZATION ---

st.subheader("Sensitivity Analysis: Option Value vs Underlying Price")
st.write("This chart illustrates how the option value evolves based on changes in the stock price.")

# Generate price range around the current spot (from -50% to +50%)
s_range = np.linspace(S*0.5, S*1.5, 50)
# Calculate option price for each point in the range
prices_range = [black_scholes(s, K, T, r, sigma, opt_type)[0] for s in s_range]

# Create interactive chart with Plotly
fig = go.Figure()
fig.add_trace(go.Scatter(
    x=s_range, 
    y=prices_range, 
    mode='lines', 
    name="Option Price", 
    line=dict(color='#00FFCC', width=3)
))

# Add a vertical line for the current spot price
fig.add_vline(x=S, line_dash="dash", line_color="white", annotation_text="Current Spot Price")

fig.update_layout(
    template="plotly_dark", 
    xaxis_title="Underlying Asset Price", 
    yaxis_title="Option Value",
    margin=dict(l=20, r=20, t=20, b=20)
)

st.plotly_chart(fig, use_container_width=True)

st.caption("Source: Black-Scholes-Merton Model. Calculations performed using SciPy's normal cumulative distribution.")
