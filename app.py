import streamlit as st

# --- CONFIGURATION GLOBALE ---
st.set_page_config(
    page_title="Quant Finance Portfolio",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- STYLE CSS PERSONNALISÉ (Le "Boost" visuel) ---
st.markdown("""
    <style>
    /* Style des boutons et des cartes */
    .stButton>button {
        border-radius: 8px;
        height: 3em;
        transition: all 0.2s ease-in-out;
        border: 1px solid #4B5563;
    }
    .stButton>button:hover {
        border-color: #ff4b4b;
        color: #ff4b4b;
        transform: translateY(-2px);
    }
    /* Harmonisation des headers de section */
    h1, h2, h3 {
        font-family: 'Inter', sans-serif;
    }
    /* Fond des containers pour l'aspect Dashboard */
    [data-testid="stVerticalBlock"] > div:has(div.stMarkdown) {
        /* Optionnel : ajouter un léger fond ici si besoin */
    }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=100) # Logo générique
    st.markdown("### 🧭 Navigation")
    st.info("Utilisez les modules ci-contre pour explorer mes travaux en ingénierie financière.")
    st.divider()
    st.caption("Version 1.0.2 - 2026")

# --- HERO SECTION ---
st.title("📈 Quantitative Finance & Risk Analysis")
st.subheader("Bridging Financial Theory and Data Engineering")

st.markdown("""
Welcome! This platform is a curated collection of financial models and interactive tools.  
It reflects my journey in exploring market mechanics, credit risk, and real-time intelligence through code.
""")

st.divider()

# --- PROJECT SHOWCASE (Interactive Modules) ---
st.header("🚀 Interactive Modules")

# Première ligne
col1, col2 = st.columns(2)

with col1:
    with st.container(border=True):
        st.markdown("### 🏦 Corporate Credit Risk")
        st.markdown("""
        Evaluates company solvency using the **Altman Z-Score**. Fetches live financial statements 
        to predict potential distress.
        """)
        # CORRECTION DU NOM DE FICHIER (Basé sur image_6aa2b1.png)
        if st.button("Launch Credit Tool", use_container_width=True, key="btn_credit"):
            st.switch_page("pages/01_Credit_risk_Z-score.py")

with col2:
    with st.container(border=True):
        st.markdown("### 🧮 Option Pricing")
        st.markdown("""
        A **Black-Scholes-Merton** implementation to price European options. 
        Calculates Greeks and visualizes sensitivities.
        """)
        # CORRECTION DU NOM DE FICHIER (Basé sur image_6aa2b1.png)
        if st.button("Launch Pricing Tool", use_container_width=True, key="btn_option"):
            st.switch_page("pages/02_Option_Pricing.py")

st.write("") # Espacement

# Deuxième ligne
col3, col4 = st.columns(2)

with col3:
    with st.container(border=True):
        st.markdown("### 🗞️ Market View") 
        st.markdown("""
        Real-time terminal for **fundamental analysis**. Aggregates news, corporate agendas, 
        and key valuation metrics.
        """)
        # CORRECTION DU NOM DE FICHIER (Basé sur image_6aa2b1.png : double underscore détecté)
        if st.button("Launch Intel Tool", use_container_width=True, key="btn_market"):
            st.switch_page("pages/03__Market_view.py")

with col4:
    with st.container(border=True):
        st.markdown("### 🏗️ Work in Progress")
        st.markdown("""
        A new quantitative module is currently under development. 
        Stay tuned for advanced portfolio optimization features.
        """)
        st.button("Coming Soon...", use_container_width=True, disabled=True)

# --- ABOUT ME SECTION ---
st.header("🔍 Why This Portfolio?")
st.markdown("""
I've always believed that finance is best understood when you can **build and break the models yourself**. 
For me, it's not just about reading formulas; it's about seeing how they react to real-time market shifts.
""")

# --- TECHNICAL TOOLKIT (Optimisé via boucle) ---
st.divider()
st.header("🛠 Technical Toolkit")
skills = {
    "Finance & Math": "Quant Research, Options Greeks, Credit Scoring, Probability.",
    "Data Stack": "Python (Pandas, NumPy, SciPy), REST APIs, YFinance.",
    "Visualization": "Streamlit, Plotly Interactive Charts, LaTeX.",
    "AI Engineering": "LLMs for code optimization, debugging, and rapid prototyping."
}

cols = st.columns(4)
for i, (skill, desc) in enumerate(skills.items()):
    with cols[i]:
        st.write(f"**{skill}**")
        st.caption(desc)

# --- CONTACT SECTION ---
st.divider()
st.subheader("📬 Contact & Networking")
st_col1, st_col2, st_col3 = st.columns(3)

with st_col1:
    st.markdown("🔗 [LinkedIn Profile](https://www.linkedin.com/in/anthony-moubarak-1771a7251/)")
with st_col2:
    st.markdown("💻 [GitHub Repository](https://github.com/TonySerenade/Finance_Board)")
with st_col3:
    st.markdown(f"📫 [Email Me](mailto:anthony.moubarak14@gmail.com)")

st.markdown("<br><center>© 2026 - Finance Board | Built with Passion</center>", unsafe_allow_html=True)
