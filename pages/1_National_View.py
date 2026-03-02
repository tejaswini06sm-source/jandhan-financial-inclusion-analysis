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

with open(os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "style.css"), encoding="utf-8") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

@st.cache_data
def get_data():
    df = load_state_data()
    df = cluster_states(df)
    df = predict_underperformers(df)
    return df

df = get_data()

# ── SIDEBAR FILTERS ──
with st.sidebar:
    st.markdown("## 🗺️ National View")
    st.markdown("---")
    st.markdown("---")

    st.markdown("### 🔽 Filters")

    search = st.text_input("🔍 Search State", placeholder="e.g. Bihar, Goa...")

    region_filter = st.multiselect(
        "🌏 Region",
        options=sorted(df["Region"].dropna().unique()),
        default=sorted(df["Region"].dropna().unique())
    )

    tier_filter = st.multiselect(
        "🏅 Performance Tier",
        options=["High Performer", "Developing", "Needs Attention"],
        default=["High Performer", "Developing", "Needs Attention"]
    )

    bal_min = int(df["Avg_Balance_INR"].min())
    bal_max = int(df["Avg_Balance_INR"].max())
    balance_range = st.slider("💰 Avg Balance Range (₹)", bal_min, bal_max, (bal_min, bal_max), step=100)

    cov_min = round(float(df["Accounts_Per_1000"].min()))
    cov_max = round(float(df["Accounts_Per_1000"].max()))
    coverage_range = st.slider("📊 Accounts per 1,000 Population", cov_min, cov_max, (cov_min, cov_max), step=10)

    acc_min = round(float(df["Accounts_Lakh"].min()))
    acc_max = round(float(df["Accounts_Lakh"].max()))
    accounts_range = st.slider("👥 Total Accounts (Lakh)", acc_min, acc_max, (acc_min, acc_max), step=10)

    sort_by = st.selectbox(
        "↕️ Sort Charts By",
        options=["Accounts_Per_1000", "Avg_Balance_INR", "Accounts_Lakh", "Deposit_Crore"],
        format_func=lambda x: {
            "Accounts_Per_1000": "Accounts per 1,000 Pop",
            "Avg_Balance_INR": "Avg Balance (₹)",
            "Accounts_Lakh": "Total Accounts (Lakh)",
            "Deposit_Crore": "Total Deposits (Crore)"
        }[x]
    )

    show_underperforming = st.checkbox("⚠️ Show Underperforming States Only", value=False)

    if st.button("🔄 Reset All Filters"):
        st.rerun()

    st.markdown("---")
    st.markdown(f"**Total states:** {len(df)}")

# ── APPLY FILTERS ──
filtered = df.copy()

if search:
    filtered = filtered[filtered["State"].str.contains(search, case=False, na=False)]

filtered = filtered[
    filtered["Region"].isin(region_filter) &
    filtered["Tier"].isin(tier_filter) &
    filtered["Avg_Balance_INR"].between(balance_range[0], balance_range[1]) &
    filtered["Accounts_Per_1000"].between(coverage_range[0], coverage_range[1]) &
    filtered["Accounts_Lakh"].between(accounts_range[0], accounts_range[1])
]

if show_underperforming and "Underperforming" in filtered.columns:
    filtered = filtered[filtered["Underperforming"] == True]

# ── HEADER ──
st.markdown("""
<div class='gov-header'>
    <h1 style='margin:0; font-size:24px;'>🗺️ National View — All 36 States & UTs</h1>
    <p style='margin:5px 0 0 0; opacity:0.9;'>Complete state-wise PMJDY performance across India</p>
</div>
""", unsafe_allow_html=True)

# ── ACTIVE FILTER SUMMARY ──
active = []
if search: active.append(f"Search: '{search}'")
if len(region_filter) < len(df["Region"].dropna().unique()): active.append(f"Regions: {', '.join(region_filter)}")
if len(tier_filter) < 3: active.append(f"Tiers: {', '.join(tier_filter)}")
if balance_range != (bal_min, bal_max): active.append(f"Balance: ₹{balance_range[0]:,}–₹{balance_range[1]:,}")
if coverage_range != (cov_min, cov_max): active.append(f"Coverage: {coverage_range[0]}–{coverage_range[1]}/1000")
if accounts_range != (acc_min, acc_max): active.append(f"Accounts: {accounts_range[0]}–{accounts_range[1]} Lakh")
if show_underperforming: active.append("Underperforming only")

if active:
    st.markdown(f"<div class='info-box'>🔽 <b>Active filters:</b> {' · '.join(active)} — showing <b>{len(filtered)}</b> of <b>{len(df)}</b> states</div>", unsafe_allow_html=True)

# ── KPIs ──
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("States Shown", len(filtered), f"of {len(df)} total")
col2.metric("Total Accounts", f"{filtered['Accounts'].sum()/1e7:.1f} Cr")
col3.metric("Total Deposits", f"₹{filtered['Deposit_Crore'].sum()/1e5:.1f} Lakh Cr")
if len(filtered) > 0 and filtered['Accounts'].sum() > 0:
    col4.metric("Avg Balance", f"₹{(filtered['Deposit_Crore'].sum()*1e7/filtered['Accounts'].sum()):.0f}")
    col5.metric("Avg Coverage", f"{filtered['Accounts_Per_1000'].mean():.0f}/1000")

st.markdown("<p class='source-tag'>Source: Ministry of Finance, Rajya Sabha Unstarred Question No. 239, 2024</p>", unsafe_allow_html=True)

if len(filtered) == 0:
    st.warning("No states match the current filters. Please adjust your filter criteria.")
    st.stop()

st.markdown("---")

# ── CHART 1: State Rankings ──
label_map = {
    "Accounts_Per_1000": "Accounts per 1,000 Population",
    "Avg_Balance_INR": "Avg Balance (₹)",
    "Accounts_Lakh": "Total Accounts (Lakh)",
    "Deposit_Crore": "Total Deposits (Crore)"
}

st.markdown(f"#### 🏆 State Rankings — {label_map[sort_by]}")
st.markdown("<div class='info-box'>This shows how many PMJDY accounts exist per 1,000 people in each state — a fairer comparison than raw totals, which favour large states.</div>", unsafe_allow_html=True)

fig = px.bar(
    filtered.sort_values(sort_by),
    x=sort_by, y="State",
    color="Tier",
    color_discrete_map={"High Performer": "#2A9D8F", "Developing": "#F4A261", "Needs Attention": "#E76F51"},
    orientation="h",
    hover_data={"Accounts": ":,", "Deposit_Crore": ":.1f", "Region": True, "Avg_Balance_INR": ":,"},
    labels={sort_by: label_map[sort_by], "State": ""},
    height=max(400, len(filtered) * 22)
)
fig.update_layout(plot_bgcolor="#F8F9FA", paper_bgcolor="white", legend_title="Performance Tier")
if sort_by == "Accounts_Per_1000":
    fig.add_vline(x=200, line_dash="dash", line_color="#E74C3C", annotation_text="200/1000 target")
st.plotly_chart(fig, use_container_width=True)

with st.expander("📖 What does this mean?"):
    st.markdown("""
    - States above **200 accounts per 1,000** are considered high-coverage areas
    - Small UTs like **Andaman & Nicobar** show very high per-capita numbers due to tiny populations
    - Large states like **UP and Bihar** have lower per-capita rates despite the most total accounts
    - **Kerala and Goa** stand out as genuine high performers — high coverage AND high average balances
    """)

st.markdown("---")

# ── CHART 2: Scatter ──
st.markdown("#### 💰 Total Accounts vs Average Balance — Who's Really Winning?")
st.markdown("<div class='info-box'>A state can have millions of accounts but tiny balances. This reveals which states have both quantity AND quality.</div>", unsafe_allow_html=True)

color_by = st.radio("Color scatter by:", ["Region", "Tier"], horizontal=True)

fig2 = px.scatter(
    filtered,
    x="Accounts_Lakh", y="Avg_Balance_INR",
    size="Deposit_Crore",
    color=color_by,
    color_discrete_map={"High Performer": "#2A9D8F", "Developing": "#F4A261", "Needs Attention": "#E76F51"} if color_by == "Tier" else None,
    hover_name="State",
    hover_data={"Accounts_Per_1000": True, "Tier": True, "Region": True},
    labels={"Accounts_Lakh": "Total Accounts (Lakh)", "Avg_Balance_INR": "Avg Balance per Account (₹)"},
    height=500, size_max=60
)
fig2.update_layout(plot_bgcolor="#F8F9FA", paper_bgcolor="white")
st.plotly_chart(fig2, use_container_width=True)

with st.expander("📖 What does this mean?"):
    st.markdown("""
    - **Top-right** = best performers: many accounts AND high balances
    - **Top-left** = small but active: few accounts but people keep money in them
    - **Bottom-right** = concerning: huge numbers but money doesn't stay
    - Bubble **size** = total deposits
    """)

st.markdown("---")

# ── CHART 3: Region Summary ──
st.markdown("#### 🧭 Region-wise Performance Summary")

region_metric = st.radio("Show region chart by:", ["Avg Balance (₹)", "Accounts per 1,000", "Total Deposits (Cr)"], horizontal=True)
metric_col = {"Avg Balance (₹)": "Avg_Balance_INR", "Accounts per 1,000": "Accounts_Per_1000", "Total Deposits (Cr)": "Deposit_Crore"}[region_metric]

region_summary = filtered.groupby("Region").agg(
    Avg_Balance_INR=("Avg_Balance_INR", "mean"),
    Accounts_Per_1000=("Accounts_Per_1000", "mean"),
    Deposit_Crore=("Deposit_Crore", "sum")
).reset_index().round(0)

fig3 = px.bar(region_summary.sort_values(metric_col), x="Region", y=metric_col,
              color=metric_col, color_continuous_scale="Blues", text=metric_col,
              labels={metric_col: region_metric}, height=400)
fmt = "₹%{text:,.0f}" if "Balance" in region_metric else "%{text:,.0f}"
fig3.update_traces(texttemplate=fmt, textposition="outside")
fig3.update_layout(plot_bgcolor="#F8F9FA", paper_bgcolor="white", coloraxis_showscale=False)
st.plotly_chart(fig3, use_container_width=True)

st.markdown("---")

# ── FULL DATA TABLE ──
st.markdown("#### 📋 Full State Data Table")

col1, col2 = st.columns([2, 1])
with col1:
    table_sort = st.selectbox("Sort table by:",
        ["Avg_Balance_INR", "Accounts_Per_1000", "Accounts_Lakh", "Deposit_Crore", "State"],
        format_func=lambda x: {"Avg_Balance_INR": "Avg Balance", "Accounts_Per_1000": "Coverage/1000",
                                "Accounts_Lakh": "Total Accounts", "Deposit_Crore": "Total Deposits", "State": "State Name"}[x])
with col2:
    sort_order = st.radio("Order:", ["Descending", "Ascending"], horizontal=True)

available_cols = [c for c in ["State", "Region", "Tier", "Accounts_Lakh", "Deposit_Crore", "Avg_Balance_INR", "Accounts_Per_1000", "Coverage_Pct", "Gap_Lakh"] if c in filtered.columns]
show_cols = st.multiselect("Columns to show:", options=available_cols,
    default=[c for c in ["State", "Region", "Tier", "Accounts_Lakh", "Avg_Balance_INR", "Accounts_Per_1000"] if c in available_cols])

if show_cols:
    sort_col = table_sort if table_sort in filtered.columns else show_cols[0]
    display_df = filtered[show_cols].sort_values(sort_col, ascending=(sort_order == "Ascending")).reset_index(drop=True)
    display_df.index = display_df.index + 1
    st.dataframe(display_df, use_container_width=True, height=400)

# ── COVERAGE GAP TABLE ──
if "Underperforming" in filtered.columns:
    st.markdown("---")
    st.markdown("#### ⚠️ Coverage Gap Analysis")
    st.markdown("<div class='info-box'>Assuming a 45% target coverage of population, this shows how many more accounts each state needs to open.</div>", unsafe_allow_html=True)
    gap_cols = [c for c in ["State", "Region", "Coverage_Pct", "Gap_Lakh", "Tier"] if c in filtered.columns]
    gap_df = filtered[filtered["Underperforming"] == True][gap_cols].sort_values("Gap_Lakh", ascending=False).reset_index(drop=True)
    gap_df.index = gap_df.index + 1
    if "Gap_Lakh" in gap_df.columns:
        st.dataframe(gap_df.style.background_gradient(subset=["Gap_Lakh"], cmap="Reds"), use_container_width=True, height=400)

# ── DOWNLOAD ──
st.markdown("---")
col1, col2 = st.columns(2)
with col1:
    st.download_button("⬇️ Download Filtered Data (CSV)", filtered.to_csv(index=False), "pmjdy_filtered_states.csv", "text/csv")
with col2:
    st.download_button("⬇️ Download Full Dataset (CSV)", df.to_csv(index=False), "pmjdy_all_states.csv", "text/csv")

st.markdown("---")
st.markdown("<div class='gov-footer'>🏦 PMJDY Dashboard · Source: Ministry of Finance, GoI · Data: 2024</div>", unsafe_allow_html=True)