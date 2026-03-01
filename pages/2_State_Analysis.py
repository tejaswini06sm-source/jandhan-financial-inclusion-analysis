import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys, os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.data_loader import load_state_data

st.set_page_config(page_title="State Analysis — PMJDY", page_icon="📊", layout="wide")

with open(os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "style.css")) as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

@st.cache_data
def get_data():
    return load_state_data()

df = get_data()

with st.sidebar:
    st.markdown("## 📊 State Analysis")
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
    selected_state = st.selectbox("🔍 Select a State", sorted(df["State"].tolist()))
    st.markdown("---")
    compare_mode = st.checkbox("Compare with another state")
    if compare_mode:
        compare_state = st.selectbox("Compare with", [s for s in sorted(df["State"].tolist()) if s != selected_state])

st.markdown("""
<div class='gov-header'>
    <h1 style='margin:0; font-size:24px;'>📊 State Deep Dive</h1>
    <p style='margin:5px 0 0 0; opacity:0.9;'>Detailed analysis for any state — accounts, deposits, rankings, and peer comparison</p>
</div>
""", unsafe_allow_html=True)

state_data = df[df["State"] == selected_state].iloc[0]

# ── STATE SCORECARD ──
st.markdown(f"## 📋 {selected_state} — Scorecard")

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Total Accounts", f"{state_data['Accounts']/1e5:.1f} Lakh")
col2.metric("Total Deposits", f"₹{state_data['Deposit_Crore']:.0f} Cr")
col3.metric("Avg Balance", f"₹{state_data['Avg_Balance_INR']:.0f}")
col4.metric("Accounts/1000 pop", f"{state_data['Accounts_Per_1000']:.1f}")
col5.metric("Performance Score", f"{state_data['Performance_Score']:.1f}/100")

col1, col2, col3 = st.columns(3)
col1.markdown(f"**National Rank (Accounts):** #{state_data['Accounts_Rank']} of 36")
col2.markdown(f"**National Rank (Avg Balance):** #{state_data['Avg_Balance_Rank']} of 36")
col3.markdown(f"**Region:** {state_data['Region']}")

st.markdown("<p class='source-tag'>Source: Ministry of Finance, Rajya Sabha Q239, 2024</p>", unsafe_allow_html=True)
st.markdown("---")

# ── COMPARE MODE ──
if compare_mode:
    compare_data = df[df["State"] == compare_state].iloc[0]
    st.markdown(f"### ⚖️ {selected_state} vs {compare_state}")

    metrics = ["Accounts", "Deposit_Crore", "Avg_Balance_INR", "Accounts_Per_1000", "Performance_Score"]
    labels = ["Total Accounts", "Deposits (Cr)", "Avg Balance (₹)", "Accounts/1000", "Performance Score"]

    fig = go.Figure()
    vals1 = [state_data[m] for m in metrics]
    vals2 = [compare_data[m] for m in metrics]
    max_vals = [max(v1, v2) for v1, v2 in zip(vals1, vals2)]
    norm1 = [v/m*100 if m > 0 else 0 for v, m in zip(vals1, max_vals)]
    norm2 = [v/m*100 if m > 0 else 0 for v, m in zip(vals2, max_vals)]

    fig.add_trace(go.Bar(name=selected_state, x=labels, y=norm1, marker_color="#1F4E79",
                         text=[f"{v:,.0f}" for v in vals1], textposition="outside"))
    fig.add_trace(go.Bar(name=compare_state, x=labels, y=norm2, marker_color="#2E86AB",
                         text=[f"{v:,.0f}" for v in vals2], textposition="outside"))
    fig.update_layout(barmode="group", plot_bgcolor="#F8F9FA", paper_bgcolor="white",
                      yaxis_title="Relative Score (%)", height=400)
    st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**{selected_state}**")
        st.dataframe(pd.DataFrame({
            "Metric": labels,
            "Value": [f"{state_data[m]:,.0f}" for m in metrics]
        }), use_container_width=True, hide_index=True)
    with col2:
        st.markdown(f"**{compare_state}**")
        st.dataframe(pd.DataFrame({
            "Metric": labels,
            "Value": [f"{compare_data[m]:,.0f}" for m in metrics]
        }), use_container_width=True, hide_index=True)
    st.markdown("---")

# ── STATE IN NATIONAL CONTEXT ──
st.markdown(f"### 📍 {selected_state} in National Context")
col1, col2 = st.columns(2)

with col1:
    st.markdown("**Avg Balance vs All States**")
    fig_rank = px.bar(
        df.sort_values("Avg_Balance_INR"),
        x="Avg_Balance_INR", y="State",
        orientation="h",
        color=df.sort_values("Avg_Balance_INR")["State"].apply(lambda s: "Selected" if s == selected_state else "Others"),
        color_discrete_map={"Selected": "#E74C3C", "Others": "#AED6F1"},
        height=600,
        labels={"Avg_Balance_INR": "Avg Balance (₹)", "State": ""}
    )
    fig_rank.update_layout(showlegend=False, plot_bgcolor="#F8F9FA", paper_bgcolor="white")
    st.plotly_chart(fig_rank, use_container_width=True)

with col2:
    st.markdown("**Accounts per 1000 Population vs All States**")
    fig_pc = px.bar(
        df.sort_values("Accounts_Per_1000"),
        x="Accounts_Per_1000", y="State",
        orientation="h",
        color=df.sort_values("Accounts_Per_1000")["State"].apply(lambda s: "Selected" if s == selected_state else "Others"),
        color_discrete_map={"Selected": "#E74C3C", "Others": "#AED6F1"},
        height=600,
        labels={"Accounts_Per_1000": "Accounts per 1,000", "State": ""}
    )
    fig_pc.update_layout(showlegend=False, plot_bgcolor="#F8F9FA", paper_bgcolor="white")
    st.plotly_chart(fig_pc, use_container_width=True)

# ── PEER COMPARISON ──
st.markdown("---")
st.markdown(f"### 🤝 Regional Peers of {selected_state}")
region = state_data["Region"]
peers = df[df["Region"] == region].sort_values("Performance_Score", ascending=False)
st.dataframe(
    peers[["State", "Accounts_Lakh", "Deposit_Crore", "Avg_Balance_INR", "Accounts_Per_1000", "Performance_Score"]].rename(columns={
        "Accounts_Lakh": "Accounts (Lakh)",
        "Deposit_Crore": "Deposits (Cr)",
        "Avg_Balance_INR": "Avg Balance (₹)",
        "Accounts_Per_1000": "Per 1000 Pop",
        "Performance_Score": "Score /100"
    }).style.background_gradient(subset=["Score /100"], cmap="Greens"),
    use_container_width=True,
    hide_index=True
)

# Download
csv = df.to_csv(index=False)
st.download_button("⬇️ Download All State Data (CSV)", csv, "pmjdy_all_states.csv", "text/csv")

st.markdown("---")
st.markdown("<div class='gov-footer'>🏦 PMJDY Dashboard · Source: Ministry of Finance, GoI · Data: 2024</div>", unsafe_allow_html=True)
