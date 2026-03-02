import streamlit as st
import pandas as pd
import sys
import os

sys.path.append(os.path.dirname(__file__))
from utils.data_loader import load_state_data, load_bihar_districts, load_karnataka_districts, load_maharashtra_districts

# ── Page Config ──
st.set_page_config(
    page_title="PMJDY Financial Inclusion Dashboard",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Load CSS ──
with open(os.path.join(os.path.dirname(__file__), "assets", "style.css"), encoding="utf-8") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ── Load Data ──
@st.cache_data
def get_data():
    return load_state_data()

df = get_data()

# ══════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════
with st.sidebar:
    st.markdown("## 🏦 PMJDY Dashboard")
    st.markdown("**India's Financial Inclusion Monitor**")
    st.markdown("---")
    st.markdown("### 📌 Navigate To")
    st.page_link("app.py", label="🏠 Home")
    st.page_link("pages/1_National_View.py", label="🗺️ National View")
    st.page_link("pages/2_State_Analysis.py", label="📊 State Analysis")
    st.page_link("pages/3_District_View.py", label="🏘️ District Explorer")
    st.page_link("pages/4_Gender_Analysis.py", label="👥 Gender Analysis")
    st.page_link("pages/5_Balance_Analysis.py", label="💰 Balance Analysis")
    st.page_link("pages/6_ML_Insights.py", label="🤖 ML Insights")
    st.page_link("pages/7_Policy_Brief.py", label="📄 Policy Brief")
    st.page_link("pages/8_About.py", label="ℹ️ About")
    st.markdown("---")
    
    st.markdown("**Data Sources**")
    st.markdown("📁 Ministry of Finance, GoI")
    st.markdown("📁 Rajya Sabha Unstarred Questions")
    st.markdown("🗓️ Data as of: **2024**")
    st.markdown("---")
    st.markdown("<small>Built with real government data. Not affiliated with GoI.</small>", unsafe_allow_html=True)

# ══════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════
st.markdown("""
<div class='gov-header'>
    <h1 style='margin:0; font-size:28px;'>🏦 Pradhan Mantri Jan Dhan Yojana</h1>
    <h2 style='margin:5px 0 0 0; font-size:18px; font-weight:400; opacity:0.9;'>
        Financial Inclusion Analysis Dashboard — India
    </h2>
    <p style='margin:8px 0 0 0; font-size:13px; opacity:0.8;'>
        Real data from Ministry of Finance · 36 States & UTs · 104 Districts (Bihar, Karnataka, Maharashtra)
    </p>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════
# WHAT IS PMJDY — INTRO
# ══════════════════════════════════════════════
with st.expander("📖 What is PMJDY? — Click to read", expanded=True):
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("""
        **Pradhan Mantri Jan Dhan Yojana (PMJDY)** is India's flagship financial inclusion program,
        launched on **28 August 2014** by Prime Minister Narendra Modi. Its core mission: ensure every
        household in India has access to a bank account, credit, insurance, and pension.

        **What it offers every account holder:**
        - ✅ Zero-balance savings account
        - ✅ RuPay debit card with ₹2 lakh accident insurance
        - ✅ ₹10,000 overdraft facility (for active accounts)
        - ✅ Direct Benefit Transfer (DBT) — government subsidies directly to account
        - ✅ Access to micro-insurance & pension schemes

        **Why it matters:** Before PMJDY, over 40% of Indian adults had no bank account.
        Cash-based welfare was leaky — money meant for the poor was lost to middlemen.
        PMJDY was designed to fix that by making every citizen a direct recipient.

        **The challenge this dashboard examines:** Opening accounts is easy.
        *Keeping them active* is hard. A large proportion of PMJDY accounts remain
        zero-balance — money goes in (wages, subsidies) and comes straight out.
        This dashboard asks: **why, and where?**
        """)
    with col2:
        st.markdown("""
        **Key Milestones**

        🗓️ **Aug 2014** — PMJDY launched

        🗓️ **2015** — 17.5 crore accounts opened in first year

        🗓️ **2018** — Overdraft limit doubled to ₹10,000

        🗓️ **2020** — COVID relief via DBT to PMJDY accounts

        🗓️ **2022** — Extended to 2025

        🗓️ **2024** — 45.8 crore accounts, ₹2.31 lakh crore deposits

        ---
        **Global Context**

        India's financial inclusion rate jumped from **53%** (2014) to **80%+** (2024)
        — one of the fastest expansions globally.
        """)

# ══════════════════════════════════════════════
# NATIONAL KPI STRIP
# ══════════════════════════════════════════════
st.markdown("---")
st.markdown("### 📊 National Snapshot — As of 2024")

total_accounts = df["Accounts"].sum()
total_deposit = df["Deposit_Crore"].sum()
avg_balance = (total_deposit * 1e7 / total_accounts)
top_state = df.loc[df["Accounts"].idxmax(), "State"]
best_balance_state = df.loc[df["Avg_Balance_INR"].idxmax(), "State"]

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Total PMJDY Accounts", f"{total_accounts/1e7:.1f} Cr", "Across 36 States/UTs")
col2.metric("Total Deposits", f"₹{total_deposit/1e5:.1f} Lakh Cr", "Real money in accounts")
col3.metric("Avg Balance / Account", f"₹{avg_balance:.0f}", "National average")
col4.metric("Largest State", top_state, "By number of accounts")
col5.metric("Best Avg Balance", best_balance_state, "Highest avg per account")

st.markdown("<p class='source-tag'>Source: Ministry of Finance, Rajya Sabha Unstarred Question, 2024</p>", unsafe_allow_html=True)

# ══════════════════════════════════════════════
# KEY FINDINGS SUMMARY
# ══════════════════════════════════════════════
st.markdown("---")
st.markdown("### 🔍 Key Findings At a Glance")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class='kpi-card'>
        <h4 style='color:#1F4E79; margin:0'>📈 Account Growth</h4>
        <p style='font-size:28px; font-weight:700; color:#2E86AB; margin:8px 0'>45.8 Crore</p>
        <p style='margin:0; font-size:14px;'>accounts opened since 2014.
        UP leads with 8.1 crore, followed by West Bengal (4.5 Cr) and Bihar (5.1 Cr).</p>
        <p style='margin:8px 0 0 0; font-size:12px; color:#27AE60;'>▲ World's largest financial inclusion drive</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class='kpi-card'>
        <h4 style='color:#1F4E79; margin:0'>⚠️ The Activation Gap</h4>
        <p style='font-size:28px; font-weight:700; color:#E74C3C; margin:8px 0'>~37%</p>
        <p style='margin:0; font-size:14px;'>of PMJDY accounts estimated as zero-balance or inactive.
        Karnataka data shows 27% inactive in some districts.</p>
        <p style='margin:8px 0 0 0; font-size:12px; color:#E74C3C;'>▼ Accounts opened ≠ accounts used</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class='kpi-card'>
        <h4 style='color:#1F4E79; margin:0'>💰 Balance Inequality</h4>
        <p style='font-size:28px; font-weight:700; color:#F39C12; margin:8px 0'>6.4x</p>
        <p style='margin:0; font-size:14px;'>gap between highest avg balance state (Goa: ₹7,611)
        and lowest (Nagaland: ₹2,804). Geography shapes financial behaviour.</p>
        <p style='margin:8px 0 0 0; font-size:12px; color:#F39C12;'>◆ Not just about opening accounts</p>
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════
# QUICK STATE RANKINGS PREVIEW
# ══════════════════════════════════════════════
st.markdown("---")
st.markdown("### 🏆 State Performance Quick View")

col1, col2 = st.columns(2)

with col1:
    st.markdown("**Top 5 States by Avg Balance per Account**")
    top5 = df.nlargest(5, "Avg_Balance_INR")[["State", "Avg_Balance_INR", "Accounts_Lakh"]].reset_index(drop=True)
    top5.index = top5.index + 1
    top5.columns = ["State", "Avg Balance (₹)", "Accounts (Lakh)"]
    st.dataframe(top5, use_container_width=True)

with col2:
    st.markdown("**Bottom 5 States by Avg Balance per Account**")
    bot5 = df.nsmallest(5, "Avg_Balance_INR")[["State", "Avg_Balance_INR", "Accounts_Lakh"]].reset_index(drop=True)
    bot5.index = bot5.index + 1
    bot5.columns = ["State", "Avg Balance (₹)", "Accounts (Lakh)"]
    st.dataframe(bot5, use_container_width=True)

# ══════════════════════════════════════════════
# HOW TO USE THIS DASHBOARD
# ══════════════════════════════════════════════
st.markdown("---")
st.markdown("### 🧭 How to Use This Dashboard")

col1, col2 = st.columns(2)
with col1:
    st.markdown("""
    **🗺️ National View**
    See all 36 states ranked, mapped, and compared. Find which regions are leading and which are lagging.

    **📊 State Analysis**
    Deep dive into any individual state — accounts, deposits, per capita performance, and peer comparison.
    """)
with col2:
    st.markdown("""
    **🏘️ District Explorer**
    Compare districts across Bihar, Karnataka & Maharashtra. Search, filter, and download.

    **🤖 ML Insights**
    Machine learning identifies underperformers, growth trajectories, and anomalies in the data.
    """)

# ══════════════════════════════════════════════
# WHO SHOULD READ THIS
# ══════════════════════════════════════════════
st.markdown("---")
col1, col2 = st.columns([2,1])
with col1:
    st.markdown("""
    <div class='info-box'>
        <b>👥 Who is this for?</b><br><br>
        🏛️ <b>Policy Researchers</b> — Understand where financial inclusion is working and where it isn't<br>
        📰 <b>Journalists</b> — Data-backed stories on India's banking access gap<br>
        🎓 <b>Students & Academics</b> — Real government data for research and analysis<br>
        🏦 <b>Banking Professionals</b> — Identify underserved districts for branch/BC expansion<br>
        🧑‍💼 <b>Government Officials</b> — Monitor PMJDY progress at state and district level
    </div>
    """, unsafe_allow_html=True)
with col2:
    st.markdown("""
    <div class='warning-box'>
        <b>⚠️ Data Note</b><br><br>
        All data sourced from official government documents (Ministry of Finance, Rajya Sabha records).<br><br>
        District-level data available for <b>Bihar, Karnataka & Maharashtra</b> only.<br><br>
        State-level data covers all <b>36 States & UTs</b>.
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════
# FOOTER
# ══════════════════════════════════════════════
st.markdown("---")
st.markdown("<div class='gov-footer'>🏦 PMJDY Financial Inclusion Dashboard &nbsp;|&nbsp; Independent Research Project &nbsp;|&nbsp; Built by Tejaswini S S Mathpati &nbsp;|&nbsp; 2026</div>", unsafe_allow_html=True)

# Back to top
st.markdown("""
<a href='#' style='position:fixed; bottom:20px; right:20px; background:#1F4E79;
color:white; padding:8px 14px; border-radius:20px; text-decoration:none;
font-size:13px; box-shadow: 0 2px 8px rgba(0,0,0,0.3);'>⬆ Top</a>
""", unsafe_allow_html=True)
