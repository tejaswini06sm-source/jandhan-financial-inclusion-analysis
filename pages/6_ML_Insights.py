import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import sys, os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.data_loader import load_state_data, load_maharashtra_districts
from utils.ml_models import cluster_states, predict_underperformers, growth_predictor, detect_anomalies

st.set_page_config(page_title="ML Insights — PMJDY", page_icon="🤖", layout="wide")

with open(os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "style.css")) as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

@st.cache_data
def get_data():
    df = load_state_data()
    df = cluster_states(df)
    df = predict_underperformers(df)
    maha = load_maharashtra_districts()
    return df, maha

df, maha = get_data()

with st.sidebar:
    st.markdown("## 🤖 ML Insights")
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
    <h1 style='margin:0; font-size:24px;'>🤖 ML Insights — Machine Learning on PMJDY Data</h1>
    <p style='margin:5px 0 0 0; opacity:0.9;'>K-Means clustering · Growth prediction · Anomaly detection · Underperformance identification</p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class='info-box'>
<b>What this section does:</b> Applies unsupervised machine learning (K-Means clustering),
linear regression for growth prediction, z-score anomaly detection, and rule-based underperformance
identification — all on real government data. Each model is explained in plain English.
</div>
""", unsafe_allow_html=True)

st.markdown("---")
tabs = st.tabs(["🎯 State Clustering", "⚠️ Underperformers", "📈 Growth Predictor", "🔍 Anomaly Detection"])

# ══ TAB 1: CLUSTERING ══
with tabs[0]:
    st.markdown("### 🎯 K-Means State Clustering — Performance Tiers")
    st.markdown("""
    **Method:** K-Means (k=3) applied to accounts per 1000 population + avg balance + performance score.
    States are grouped into 3 natural clusters based on their actual data — not manual categorization.
    """)

    tier_colors = {"High Performer": "#2A9D8F", "Developing": "#F4A261", "Needs Attention": "#E76F51"}

    col1, col2 = st.columns(2)
    with col1:
        fig = px.scatter(
            df, x="Accounts_Per_1000", y="Avg_Balance_INR",
            color="Tier", size="Deposit_Crore",
            hover_name="State",
            color_discrete_map=tier_colors,
            labels={"Accounts_Per_1000": "Accounts per 1,000 Population", "Avg_Balance_INR": "Avg Balance (₹)"},
            height=450, title="State Clusters — Coverage vs Balance"
        )
        fig.update_layout(plot_bgcolor="#F8F9FA", paper_bgcolor="white")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        tier_summary = df.groupby("Tier").agg(
            States=("State", "count"),
            Avg_Coverage=("Accounts_Per_1000", "mean"),
            Avg_Balance=("Avg_Balance_INR", "mean"),
            Total_Accounts=("Accounts", "sum")
        ).reset_index().round(1)
        st.markdown("**Cluster Summary**")
        st.dataframe(tier_summary, use_container_width=True, hide_index=True)

        st.markdown("**States by Tier**")
        for tier in ["High Performer", "Developing", "Needs Attention"]:
            states = df[df["Tier"] == tier]["State"].tolist()
            color = {"High Performer": "🟢", "Developing": "🟡", "Needs Attention": "🔴"}[tier]
            with st.expander(f"{color} {tier} ({len(states)} states)"):
                st.write(", ".join(sorted(states)))

    with st.expander("📖 How does K-Means work here?"):
        st.markdown("""
        1. Each state is represented as a point in 3D space: (accounts per 1000, avg balance, performance score)
        2. K-Means finds 3 cluster centers that minimize within-cluster distances
        3. Each state is assigned to its nearest cluster center
        4. Clusters are labeled based on which has highest/lowest avg balance
        5. **Limitation:** With only 36 data points, clusters should be interpreted as approximate groupings, not definitive labels
        """)

# ══ TAB 2: UNDERPERFORMERS ══
with tabs[1]:
    st.markdown("### ⚠️ Underperformance Analysis — States Not Meeting Their Potential")
    st.markdown("""
    **Method:** A state is considered underperforming if its actual accounts are below 45% of its projected population
    (a reasonable financial inclusion target for a state's adult population).
    """)

    under_df = df[df["Underperforming"] == True].sort_values("Gap_Lakh", ascending=False)
    over_df = df[df["Underperforming"] == False].sort_values("Coverage_Pct", ascending=False)

    col1, col2 = st.columns(2)
    col1.metric("States Below 45% Coverage Target", len(under_df))
    col2.metric("States At/Above Target", len(over_df))

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**States Underperforming — Coverage Gap**")
        fig = px.bar(
            under_df.head(15).sort_values("Gap_Lakh"),
            x="Gap_Lakh", y="State",
            orientation="h",
            color="Coverage_Pct",
            color_continuous_scale="Reds_r",
            labels={"Gap_Lakh": "Accounts Gap (Lakh)", "Coverage_Pct": "Current Coverage %"},
            height=450
        )
        fig.update_layout(plot_bgcolor="#F8F9FA", paper_bgcolor="white")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("**Coverage % vs Target (45%)**")
        all_states = df.sort_values("Coverage_Pct")
        fig2 = px.bar(
            all_states,
            x="Coverage_Pct", y="State",
            orientation="h",
            color=all_states["Coverage_Pct"].apply(lambda x: "Above Target" if x >= 45 else "Below Target"),
            color_discrete_map={"Above Target": "#2A9D8F", "Below Target": "#E76F51"},
            labels={"Coverage_Pct": "Population Coverage (%)", "State": ""},
            height=700
        )
        fig2.add_vline(x=45, line_dash="dash", line_color="#1F4E79", annotation_text="45% target")
        fig2.update_layout(plot_bgcolor="#F8F9FA", paper_bgcolor="white")
        st.plotly_chart(fig2, use_container_width=True)

# ══ TAB 3: GROWTH PREDICTOR ══
with tabs[2]:
    st.markdown("### 📈 Growth Rate Predictor — Maharashtra Districts")
    st.markdown("""
    **Method:** Linear regression fitted on 3 data points (March 2022, 2023, 2024) per district.
    Projects the annual growth rate and estimates when each district will reach 120% of current accounts (proxy for saturation).
    """)

    growth_df = growth_predictor(maha)
    growth_df = growth_df.dropna(subset=["Annual_Growth"])

    col1, col2 = st.columns(2)
    col1.metric("Avg Annual Growth (Maharashtra)", f"{growth_df['Annual_Growth'].mean():,.0f} accounts/year")
    col2.metric("Fastest Growing District", growth_df.loc[growth_df["Annual_Growth"].idxmax(), "District"])

    col1, col2 = st.columns(2)
    with col1:
        fig = px.bar(
            growth_df.sort_values("Annual_Growth"),
            x="Annual_Growth", y="District",
            orientation="h",
            color="Annual_Growth",
            color_continuous_scale="Blues",
            labels={"Annual_Growth": "Annual Account Growth (accounts/yr)", "District": ""},
            height=600,
            title="Projected Annual Growth by District"
        )
        fig.update_layout(plot_bgcolor="#F8F9FA", paper_bgcolor="white")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        valid_years = growth_df.dropna(subset=["Target_Year"])
        valid_years = valid_years[valid_years["Target_Year"] < 2035]
        fig2 = px.bar(
            valid_years.sort_values("Target_Year"),
            x="Target_Year", y="District",
            orientation="h",
            color="Target_Year",
            color_continuous_scale="RdYlGn_r",
            labels={"Target_Year": "Projected Year to Reach 120% of Current", "District": ""},
            height=600,
            title="When Will Districts Reach Growth Target?"
        )
        fig2.update_layout(plot_bgcolor="#F8F9FA", paper_bgcolor="white")
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("**Full Growth Prediction Table**")
    st.dataframe(
        growth_df[["District", "Current_Accounts", "Annual_Growth", "Growth_Pct_2yr", "Target_Year"]].rename(columns={
            "Current_Accounts": "Current Accounts",
            "Annual_Growth": "Annual Growth",
            "Growth_Pct_2yr": "2-Yr Growth %",
            "Target_Year": "Target Year"
        }).sort_values("Annual Growth", ascending=False).reset_index(drop=True).style.background_gradient(subset=["Annual Growth"], cmap="Blues"),
        use_container_width=True
    )

# ══ TAB 4: ANOMALY DETECTION ══
with tabs[3]:
    st.markdown("### 🔍 Anomaly Detection — Which States Behave Unusually?")
    st.markdown("""
    **Method:** Z-score standardization. States with |z-score| > 2 are flagged as anomalies —
    meaning they are more than 2 standard deviations from the mean in accounts or balance.
    These deserve special investigation.
    """)

    anomaly_df = detect_anomalies(df.reset_index(drop=True), "Accounts")
    anomaly_df2 = detect_anomalies(df.reset_index(drop=True), "Avg_Balance_INR")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Account Volume Anomalies**")
        fig = px.scatter(
            anomaly_df,
            x="State", y="Accounts",
            color="Anomaly_Type",
            color_discrete_map={"Normal": "#2A9D8F", "Unusually High": "#E76F51", "Unusually Low": "#F4A261"},
            size="Accounts",
            hover_data={"Z_Score": ":.2f", "Region": True},
            height=450,
            title="States by Account Volume — Anomalies Highlighted"
        )
        fig.update_layout(plot_bgcolor="#F8F9FA", paper_bgcolor="white",
                          xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("**Average Balance Anomalies**")
        fig2 = px.scatter(
            anomaly_df2,
            x="State", y="Avg_Balance_INR",
            color="Anomaly_Type",
            color_discrete_map={"Normal": "#2A9D8F", "Unusually High": "#E76F51", "Unusually Low": "#F4A261"},
            size="Avg_Balance_INR",
            hover_data={"Z_Score": ":.2f", "Region": True},
            height=450,
            title="States by Avg Balance — Anomalies Highlighted"
        )
        fig2.update_layout(plot_bgcolor="#F8F9FA", paper_bgcolor="white",
                           xaxis_tickangle=-45)
        st.plotly_chart(fig2, use_container_width=True)

    flagged = anomaly_df[anomaly_df["Anomaly"] == True][["State", "Accounts", "Avg_Balance_INR", "Z_Score", "Anomaly_Type"]]
    if len(flagged) > 0:
        st.markdown("**Flagged Anomalous States**")
        st.dataframe(flagged.reset_index(drop=True), use_container_width=True, hide_index=True)
        with st.expander("📖 Why are these states anomalous?"):
            st.markdown("""
            - **Large states** like UP, Bihar, West Bengal naturally appear as high-account anomalies — they have enormous populations
            - **Small UTs** like Lakshadweep, Andaman appear as low-account anomalies — tiny populations
            - These aren't necessarily problems — they're structural features of India's demographic diversity
            - What's more concerning is states with anomalously LOW average balances relative to their size
            """)

st.markdown("---")
st.markdown("<div class='gov-footer'>🏦 PMJDY Dashboard · ML: K-Means, Linear Regression, Z-Score · Real government data · 2024</div>", unsafe_allow_html=True)
