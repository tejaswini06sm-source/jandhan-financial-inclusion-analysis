import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import sys, os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.data_loader import load_state_data
from utils.ml_models import cluster_states, predict_underperformers

st.set_page_config(page_title="National View — PMJDY", page_icon="🗺️", layout="wide")

with open(os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "style.css")) as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

@st.cache_data
def get_data():
    df = load_state_data()
    df = cluster_states(df)
    df = predict_underperformers(df)
    return df

df = get_data()

# Sidebar
with st.sidebar:
    st.markdown("## 🗺️ National View")
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
    st.markdown("---")
    region_filter = st.multiselect("Filter by Region", options=sorted(df["Region"].dropna().unique()), default=sorted(df["Region"].dropna().unique()))
    tier_filter = st.multiselect("Filter by Tier", options=["High Performer", "Developing", "Needs Attention"], default=["High Performer", "Developing", "Needs Attention"])

filtered = df[df["Region"].isin(region_filter) & df["Tier"].isin(tier_filter)]

# Header
st.markdown("""
<div class='gov-header'>
    <h1 style='margin:0; font-size:24px;'>🗺️ National View — All 36 States & UTs</h1>
    <p style='margin:5px 0 0 0; opacity:0.9;'>Complete state-wise PMJDY performance across India</p>
</div>
""", unsafe_allow_html=True)

# KPIs
col1, col2, col3, col4 = st.columns(4)
col1.metric("States Shown", len(filtered), f"of 36 total")
col2.metric("Total Accounts", f"{filtered['Accounts'].sum()/1e7:.1f} Cr")
col3.metric("Total Deposits", f"₹{filtered['Deposit_Crore'].sum()/1e5:.1f} Lakh Cr")
col4.metric("Avg Balance", f"₹{(filtered['Deposit_Crore'].sum()*1e7/filtered['Accounts'].sum()):.0f}")

st.markdown("<p class='source-tag'>Source: Ministry of Finance, Rajya Sabha Unstarred Question No. 239, 2024</p>", unsafe_allow_html=True)

st.markdown("---")

# ── CHART 1: State Rankings Bar Chart ──
st.markdown("#### 🏆 State Rankings — Accounts per 1,000 Population")
st.markdown("<div class='info-box'>This shows how many PMJDY accounts exist per 1,000 people in each state — a fairer comparison than raw totals, which favour large states.</div>", unsafe_allow_html=True)

fig = px.bar(
    filtered.sort_values("Accounts_Per_1000"),
    x="Accounts_Per_1000", y="State",
    color="Tier",
    color_discrete_map={"High Performer": "#2A9D8F", "Developing": "#F4A261", "Needs Attention": "#E76F51"},
    orientation="h",
    hover_data={"Accounts": ":,", "Deposit_Crore": ":.1f", "Region": True},
    labels={"Accounts_Per_1000": "Accounts per 1,000 Population", "State": ""},
    height=700,
    title=""
)
fig.update_layout(plot_bgcolor="#F8F9FA", paper_bgcolor="white", legend_title="Performance Tier")
fig.add_vline(x=200, line_dash="dash", line_color="#E74C3C", annotation_text="200 accounts/1000 target")
st.plotly_chart(fig, use_container_width=True)

with st.expander("📖 What does this mean?"):
    st.markdown("""
    - States above **200 accounts per 1,000** are considered high-coverage areas
    - Small UTs like **Andaman & Nicobar** and **Lakshadweep** show very high per-capita numbers due to tiny populations
    - Large states like **UP and Bihar** have lower per-capita rates despite having the most total accounts
    - **Kerala and Goa** stand out as genuine high performers — high coverage AND high average balances
    """)

st.markdown("---")

# ── CHART 2: Deposits vs Accounts Scatter ──
st.markdown("#### 💰 Total Accounts vs Average Balance — Who's Really Winning?")
st.markdown("<div class='info-box'>A state can have millions of accounts but tiny balances — meaning accounts are inactive. This chart reveals which states have both quantity AND quality.</div>", unsafe_allow_html=True)

fig2 = px.scatter(
    filtered,
    x="Accounts_Lakh", y="Avg_Balance_INR",
    size="Deposit_Crore", color="Region",
    hover_name="State",
    hover_data={"Accounts_Per_1000": True, "Tier": True},
    labels={"Accounts_Lakh": "Total Accounts (Lakh)", "Avg_Balance_INR": "Avg Balance per Account (₹)"},
    height=500,
    size_max=60,
    title=""
)
fig2.update_layout(plot_bgcolor="#F8F9FA", paper_bgcolor="white")
st.plotly_chart(fig2, use_container_width=True)

with st.expander("📖 What does this mean?"):
    st.markdown("""
    - **Top-right** = best performers: many accounts AND high balances (e.g., Maharashtra, Gujarat)
    - **Top-left** = small but active states: few accounts but people keep money in them (e.g., Goa, Sikkim)
    - **Bottom-right** = concerning: huge account numbers but money doesn't stay (e.g., UP, Bihar)
    - Bubble **size** = total deposits — bigger bubble means more money held
    """)

st.markdown("---")

# ── CHART 3: Region-wise Summary ──
st.markdown("#### 🧭 Region-wise Performance Summary")

region_summary = filtered.groupby("Region").agg(
    States=("State", "count"),
    Total_Accounts=("Accounts", "sum"),
    Avg_Balance=("Avg_Balance_INR", "mean"),
    Avg_Per_1000=("Accounts_Per_1000", "mean"),
    Total_Deposits=("Deposit_Crore", "sum")
).reset_index().round(0)

fig3 = px.bar(
    region_summary.sort_values("Avg_Balance"),
    x="Region", y="Avg_Balance",
    color="Avg_Per_1000",
    color_continuous_scale="Blues",
    text="Avg_Balance",
    labels={"Avg_Balance": "Avg Balance per Account (₹)", "Avg_Per_1000": "Accounts/1000 pop"},
    height=400,
    title=""
)
fig3.update_traces(texttemplate="₹%{text:,.0f}", textposition="outside")
fig3.update_layout(plot_bgcolor="#F8F9FA", paper_bgcolor="white")
st.plotly_chart(fig3, use_container_width=True)

st.markdown("---")

# ── COVERAGE GAP TABLE ──
st.markdown("#### ⚠️ Coverage Gap Analysis — Which States Have Most Unbanked Population?")
st.markdown("<div class='info-box'>Assuming a 45% target coverage of population, this shows how many more accounts each state needs to open.</div>", unsafe_allow_html=True)

gap_df = filtered[filtered["Underperforming"] == True][["State", "Region", "Coverage_Pct", "Gap_Lakh", "Tier"]].sort_values("Gap_Lakh", ascending=False).reset_index(drop=True)
gap_df.index = gap_df.index + 1
gap_df.columns = ["State", "Region", "Coverage %", "Gap (Lakh accounts)", "Tier"]
st.dataframe(
    gap_df.style.background_gradient(subset=["Gap (Lakh accounts)"], cmap="Reds"),
    use_container_width=True,
    height=400
)

# Download button
csv = filtered.to_csv(index=False)
st.download_button("⬇️ Download Full State Data (CSV)", csv, "pmjdy_state_data.csv", "text/csv")

st.markdown("---")
st.markdown("<div class='gov-footer'>🏦 PMJDY Dashboard · Source: Ministry of Finance, GoI · Data: 2024</div>", unsafe_allow_html=True)
