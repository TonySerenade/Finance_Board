import streamlit as st
import numpy as np
from scipy.stats import norm
import pandas as pd
import plotly.graph_objects as go

# Configuration de la page Streamlit pour utiliser toute la largeur de l'écran
st.set_page_config(page_title="Option Pricing Model", layout="wide")



# --- FONCTIONS MATHÉMATIQUES (Modèle de Black-Scholes) ---

def black_scholes(S, K, T, r, sigma, option_type="call"):
    """
    S : Prix actuel du sous-jacent (Stock Price)
    K : Prix d'exercice (Strike Price)
    T : Temps restant jusqu'à l'échéance en années (Time to Maturity)
    r : Taux d'intérêt sans risque (Risk-free rate)
    sigma : Volatilité implicite du sous-jacent (Volatility)
    """
    
    # Étape 1 : Calcul de d1 et d2 (les variables de probabilité du modèle)
    # d1 représente la probabilité que l'option finisse "dans la monnaie" ajustée par le risque
    d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    # d2 est utilisé pour calculer la valeur actuelle du strike à payer à l'échéance
    d2 = d1 - sigma * np.sqrt(T)
    
    # Étape 2 : Calcul du prix de l'option selon le type
    if option_type == "call":
        # Formule du Call : S*N(d1) - K*exp(-rt)*N(d2)
        price = S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
        # Delta du Call : Probabilité de terminaison ITM / Sensibilité au prix du spot
        delta = norm.cdf(d1)
    else:
        # Formule du Put : K*exp(-rt)*N(-d2) - S*N(-d1)
        price = K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
        # Delta du Put : Toujours compris entre -1 et 0
        delta = norm.cdf(d1) - 1
        
    # Étape 3 : Calcul des "Grecques" (Indicateurs de gestion des risques)
    
    # Gamma (Γ) : Sensibilité du Delta par rapport aux variations du prix du spot
    gamma = norm.pdf(d1) / (S * sigma * np.sqrt(T))
    
    # Vega (ν) : Sensibilité du prix de l'option par rapport à la volatilité
    vega = S * norm.pdf(d1) * np.sqrt(T)
    
    # Theta (θ) : Dépréciation temporelle (Time decay) - Valeur perdue chaque jour qui passe
    theta = -(S * norm.pdf(d1) * sigma) / (2 * np.sqrt(T)) - r * K * np.exp(-r * T) * norm.cdf(d2 if option_type=="call" else -d2)
    
    return price, delta, gamma, vega, theta



# --- INTERFACE UTILISATEUR STREAMLIT ---

st.title("🧮 Option Pricing & Greeks (Black-Scholes)")

# Section théorique pour le recruteur
with st.expander("📖 Contexte Théorique"):
    st.write("""
    Le modèle de Black-Scholes (1973) est le standard pour évaluer les options européennes. 
    Il repose sur l'hypothèse que les prix suivent un mouvement brownien géométrique avec une volatilité constante.
    """)
    st.latex(r"C = S_t N(d_1) - K e^{-rt} N(d_2)")

st.divider()

# Création de 3 colonnes pour organiser les paramètres d'entrée
col_in1, col_in2, col_in3 = st.columns(3)

with col_in1:
    st.markdown("**Paramètres du Marché**")
    S = st.number_input("Prix du Sous-jacent (S)", value=100.0, help="Prix actuel de l'action sur le marché")
    K = st.number_input("Prix d'Exercice (K)", value=100.0, help="Prix auquel vous pouvez acheter/vendre l'actif")

with col_in2:
    st.markdown("**Paramètres Temporels**")
    T = st.slider("Maturité (Années)", 0.01, 2.0, 0.5, help="Temps restant avant l'expiration")
    r = st.slider("Taux sans risque (%)", 0.0, 10.0, 2.0) / 100

with col_in3:
    st.markdown("**Risque & Type**")
    sigma = st.slider("Volatilité (σ) (%)", 1.0, 100.0, 20.0) / 100
    opt_type = st.selectbox("Type d'Option", ["Call", "Put"]).lower()

# Exécution du calcul financier
price, delta, gamma, vega, theta = black_scholes(S, K, T, r, sigma, opt_type)



# --- AFFICHAGE DES RÉSULTATS ---

st.subheader(f"Prix Théorique de l'Option : ${price:.2f}")

# Affichage des métriques de risque (Grecques) dans des boîtes visuelles
m1, m2, m3, m4 = st.columns(4)
m1.metric("Delta (Δ)", f"{delta:.3f}", help="Sensibilité au prix. Si S monte de 1$, l'option monte de Delta$.")
m2.metric("Gamma (Γ)", f"{gamma:.4f}", help="Stabilité du Delta. Important pour le Delta Hedging.")
m3.metric("Vega (ν)", f"{vega:.3f}", help="Sensibilité à la volatilité. Impact d'une hausse de 1% de sigma.")
m4.metric("Theta (θ)", f"{theta:.3f}", help="Impact du passage du temps (dépréciation quotidienne).")

st.divider()



# --- VISUALISATION GRAPHIQUE ---

st.subheader("Analyse de Sensibilité : Prix vs Sous-jacent")
st.write("Ce graphique montre comment la valeur de l'option évolue en fonction du prix de l'action.")

# Génération d'une plage de prix autour du spot actuel (de -50% à +50%)
s_range = np.linspace(S*0.5, S*1.5, 50)
# Calcul du prix de l'option pour chaque point de la plage
prices_range = [black_scholes(s, K, T, r, sigma, opt_type)[0] for s in s_range]

# Création du graphique interactif avec Plotly
fig = go.Figure()
fig.add_trace(go.Scatter(
    x=s_range, 
    y=prices_range, 
    mode='lines', 
    name="Prix de l'Option", 
    line=dict(color='#00FFCC', width=3)
))

# Ajout d'une ligne verticale pour marquer le prix actuel (Spot)
fig.add_vline(x=S, line_dash="dash", line_color="white", annotation_text="Prix Actuel (Spot)")

fig.update_layout(
    template="plotly_dark", 
    xaxis_title="Prix du Sous-jacent", 
    yaxis_title="Valeur de l'Option",
    margin=dict(l=20, r=20, t=20, b=20)
)

st.plotly_chart(fig, use_container_width=True)

st.caption("Source : Modèle Black-Scholes-Merton. Les calculs utilisent la distribution normale cumulée de SciPy.")
