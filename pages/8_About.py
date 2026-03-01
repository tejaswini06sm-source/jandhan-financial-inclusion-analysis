import streamlit as st
import sys, os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

st.set_page_config(page_title="About — PMJDY Dashboard", page_icon="ℹ️", layout="wide")

with open(os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "style.css")) as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## ℹ️ About")
    st.markdown("---")
    st.page_link("app.py", label="🏠 Home")
    st.page_link("pages/1_National_View.py", label="🗺️ National View")
    st.page_link("pages/2_State_Analysis.py", label="📊 State Analysis")
    st.page_link("pages/3_District_View.py", label="🏘️ District Explorer")
    st.page_link("pages/4_Gender_Analysis.py", label="👥 Gender Analysis")
    st.page_link("pages/5_Balance_Analysis.py", label="💰 Balance Analysis")
    st.page_link("pages/6_ML_Insights.py", label="🤖 ML Insights")
    st.page_link("pages/7_Policy_Brief.py", label="📄 Policy Brief")
    st.page_link("pages/8_About.py", label="ℹ️ About")

st.markdown("""
<div class='gov-header'>
    <h1 style='margin:0; font-size:24px;'>ℹ️ About This Dashboard</h1>
    <p style='margin:5px 0 0 0; opacity:0.9;'>Data sources · Methodology · Limitations · Contact</p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 👩‍💻 About the Project")
    st.markdown("""
    This dashboard was built as an independent data analysis project examining
    India's flagship financial inclusion program — PMJDY — using **real, publicly available
    government data** from Ministry of Finance and Rajya Sabha records.

    **Purpose:** To move beyond headline numbers and examine *where* financial inclusion
    is working, *where* it isn't, and *why* — using data science and machine learning.

    **Builder:** Tejaswini Shidheshwar Mathpati

    **Tools used:**
    - Python 3.12
    - Streamlit (multi-page app)
    - Plotly (interactive charts)
    - Scikit-learn (K-Means, Linear Regression)
    - SQLite (data storage)
    - GitHub + Streamlit Cloud (deployment)

    **Not affiliated with:** Government of India, Ministry of Finance, or PMJDY program.
    This is an independent academic/research project.
    """)

with col2:
    st.markdown("### 📁 Data Sources")
    st.markdown("""
    All data is sourced from official government documents. Every dataset is cited:

    | Dataset | Source Document | Coverage |
    |---------|----------------|----------|
    | Balance Distribution | RS Q230, 2024 | National |
    | State-wise Accounts | RS Q239, 2024 | 36 States/UTs |
    | Bihar Districts | RS Q246, 2022 | 38 Districts |
    | Karnataka Districts | RS Q2313, 2023 | 30 Districts |
    | Maharashtra Districts | RS Q886, 2024 | 36 Districts |

    **RS** = Rajya Sabha Unstarred Question, Ministry of Finance

    All Rajya Sabha questions are public documents available at:
    [rajyasabha.nic.in](https://rajyasabha.nic.in) and [data.gov.in](https://data.gov.in)

    **Population data** used for per-capita calculations is based on
    Census 2011 projections to 2024 (Office of the Registrar General, India).
    """)

st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### ⚠️ Data Limitations")
    st.markdown("""
    Being transparent about what this data cannot tell us:

    **1. District data is limited to 3 states**
    Bihar, Karnataka, and Maharashtra. District-level data for all other states
    is not publicly available in machine-readable format.

    **2. No zero-balance % in raw data**
    The government does not publish zero-balance rates directly.
    Inactive account estimates are derived from Karnataka's operative account data
    and should be treated as indicative, not precise.

    **3. Time periods vary**
    Bihar data = 2022, Karnataka = 2023, Maharashtra = 2022–2024, State data = 2024.
    Direct comparisons across time periods should be made cautiously.

    **4. Population projections are estimates**
    Per-capita calculations use projected 2024 populations based on
    2011 Census growth rates — these are estimates, not actual counts.

    **5. Global comparisons are approximate**
    World Bank Global Findex 2021 data used for global benchmarking
    may not perfectly align with 2024 PMJDY data.
    """)

with col2:
    st.markdown("### 🔬 Methodology")
    st.markdown("""
    **Performance Score** = weighted combination of:
    - 50% weight: Accounts per 1,000 population (normalised 0-100)
    - 50% weight: Average balance per account (normalised 0-100)

    **K-Means Clustering** (k=3):
    - Features: accounts per 1000, avg balance, performance score
    - Standardised with StandardScaler before clustering
    - Labels assigned based on cluster's mean performance score
    - Limitation: 36 data points is a small sample for clustering

    **Underperformance Detection:**
    - Threshold: 45% of state population as target PMJDY coverage
    - States below this threshold flagged as underperforming
    - Note: 45% is a reasonable but somewhat arbitrary threshold

    **Growth Prediction:**
    - Linear regression on 3 time points (2022, 2023, 2024)
    - Projects annual growth rate forward
    - 120% of current accounts used as proxy "saturation" target
    - Limitation: 3 points is insufficient for robust time-series prediction

    **Anomaly Detection:**
    - Z-score method: |z| > 2 flagged as anomaly
    - Applied to raw accounts and average balance separately
    """)

st.markdown("---")

st.markdown("### 🔗 Useful Links")
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown("""
    **Official PMJDY**
    [pmjdy.gov.in](https://pmjdy.gov.in)

    Live statistics, state-wise data, scheme details
    """)
with col2:
    st.markdown("""
    **Open Government Data**
    [data.gov.in](https://data.gov.in)

    Download official datasets used in this analysis
    """)
with col3:
    st.markdown("""
    **Rajya Sabha Questions**
    [rajyasabha.nic.in](https://rajyasabha.nic.in)

    Source documents for all district-level data
    """)
with col4:
    st.markdown("""
    **World Bank Findex**
    [worldbank.org](https://www.worldbank.org/en/publication/globalfindex)

    Global financial inclusion benchmarks
    """)

st.markdown("---")

st.markdown("### 📜 Citing This Dashboard")
st.markdown("""
```
Mathpati, T.S. (2024). PMJDY Financial Inclusion Analysis Dashboard.
Built with Streamlit. Data: Ministry of Finance, GoI.
Available at: [your streamlit URL]
```
""")

st.markdown("---")
st.markdown("""
<div class='gov-footer'>
    🏦 PMJDY Financial Inclusion Dashboard &nbsp;|&nbsp;
    Independent research project &nbsp;|&nbsp;
    Not affiliated with Government of India &nbsp;|&nbsp;
    Built by Tejaswini Shidheshwar Mathpati &nbsp;|&nbsp;
    2024
</div>
""", unsafe_allow_html=True)
