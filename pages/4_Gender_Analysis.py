import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys, os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.data_loader import load_karnataka_districts, load_state_data

st.set_page_config(page_title="Gender Analysis — PMJDY", page_icon="👥", layout="wide")

with open(os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "style.css")) as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

@st.cache_data
def get_data():
    return load_karnataka_districts(), load_state_data()

karnataka, state_df = get_data()

with st.sidebar:
    st.markdown("## 👥 Gender Analysis")
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
    st.markdown("<div class='info-box'><small>Gender-disaggregated data is available for Karnataka's 30 districts from official government sources (2023).</small></div>", unsafe_allow_html=True)

st.markdown("""
<div class='gov-header'>
    <h1 style='margin:0; font-size:24px;'>👥 Gender Analysis — Female Financial Inclusion</h1>
    <p style='margin:5px 0 0 0; opacity:0.9;'>Who holds PMJDY accounts? Are women being left behind?</p>
</div>
""", unsafe_allow_html=True)

# ── INTRO ──
st.markdown("""
<div class='info-box'>
<b>Why gender matters in financial inclusion:</b> PMJDY was explicitly designed to prioritize women —
the government targeted opening accounts for women first, especially in rural areas. But access ≠ usage.
This section examines whether women are truly included or just counted.
<br><br>
<b>Data available:</b> Karnataka district-level gender breakdown (30 districts, 2023)
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ── NATIONAL CONTEXT ──
st.markdown("### 🌍 National Gender Picture")
col1, col2, col3 = st.columns(3)

# PMJDY national stats (from official pmjdy.gov.in reports)
total_accounts = 458932822
women_accounts = 248500000  # ~54% women as per PMJDY annual report
men_accounts = total_accounts - women_accounts

col1.metric("Women Account Holders (National)", f"{women_accounts/1e7:.1f} Cr", "~54% of all accounts")
col2.metric("Men Account Holders (National)", f"{men_accounts/1e7:.1f} Cr", "~46% of all accounts")
col3.metric("Women's Share", "54.2%", "Exceeds 50% — a positive sign")

st.markdown("<p class='source-tag'>Source: PMJDY Progress Report, Ministry of Finance, 2024 (National estimate)</p>", unsafe_allow_html=True)

fig_donut = go.Figure(data=[go.Pie(
    labels=["Women", "Men"],
    values=[women_accounts, men_accounts],
    hole=0.5,
    marker_colors=["#E84393", "#1F4E79"],
    textinfo="label+percent"
)])
fig_donut.update_layout(
    title="National Gender Split — PMJDY Account Holders",
    paper_bgcolor="white",
    height=350,
    annotations=[dict(text="45.8 Cr<br>Total", x=0.5, y=0.5, font_size=14, showarrow=False)]
)
st.plotly_chart(fig_donut, use_container_width=True)

with st.expander("📖 What does this mean?"):
    st.markdown("""
    - **54% women** account holders nationally is a significant achievement — women outnumber men in PMJDY
    - This was driven by targeted government campaigns, particularly in rural areas
    - However, having an account ≠ using it. Many women's accounts are opened but remain inactive
    - The real question is: **are these accounts being used by women themselves**, or opened in their names but controlled by male relatives?
    """)

st.markdown("---")

# ── KARNATAKA DISTRICT GENDER ANALYSIS ──
st.markdown("### 📍 Karnataka District-Level Gender Analysis (30 Districts, 2023)")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Accounts", f"{karnataka['Total_Accounts'].sum()/1e5:.0f} Lakh")
col2.metric("Female Accounts", f"{karnataka['Female_Accounts'].sum()/1e5:.0f} Lakh")
col3.metric("Male Accounts", f"{karnataka['Male_Accounts'].sum()/1e5:.0f} Lakh")
col4.metric("State Female %", f"{(karnataka['Female_Accounts'].sum()/karnataka['Total_Accounts'].sum()*100):.1f}%")

st.markdown("<p class='source-tag'>Source: Rajya Sabha Unstarred Question No. 2313, March 2023</p>", unsafe_allow_html=True)

st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    st.markdown("**Female Account Share by District (%)**")
    st.markdown("*50% line = gender parity*")
    fig = px.bar(
        karnataka.sort_values("Female_Pct"),
        x="Female_Pct", y="District",
        orientation="h",
        color="Female_Pct",
        color_continuous_scale="RdYlGn",
        range_color=[40, 60],
        labels={"Female_Pct": "Female Accounts (%)", "District": ""},
        height=600
    )
    fig.add_vline(x=50, line_dash="dash", line_color="#1F4E79",
                  annotation_text="50% parity", annotation_position="top right")
    fig.update_layout(plot_bgcolor="#F8F9FA", paper_bgcolor="white")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown("**Male vs Female Accounts — Top 15 Districts**")
    top15 = karnataka.nlargest(15, "Total_Accounts").sort_values("Total_Accounts")
    fig2 = go.Figure()
    fig2.add_trace(go.Bar(name="Female", y=top15["District"], x=top15["Female_Accounts"],
                          orientation="h", marker_color="#E84393"))
    fig2.add_trace(go.Bar(name="Male", y=top15["District"], x=top15["Male_Accounts"],
                          orientation="h", marker_color="#1F4E79"))
    fig2.update_layout(barmode="group", height=600, plot_bgcolor="#F8F9FA",
                       paper_bgcolor="white", xaxis_title="Number of Accounts")
    st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")

# ── OPERATIVE ACCOUNTS BY GENDER DISTRICT ──
st.markdown("### 🔄 Operative Rate — Are Accounts Being Used?")
st.markdown("<div class='info-box'>Operative accounts = accounts with at least one transaction in the past 90 days. High operative % = active financial engagement.</div>", unsafe_allow_html=True)

fig3 = px.scatter(
    karnataka,
    x="Female_Pct", y="Operative_Pct",
    size="Total_Accounts",
    hover_name="District",
    color="Inactive_Pct",
    color_continuous_scale="RdYlGn_r",
    labels={
        "Female_Pct": "Female Account Share (%)",
        "Operative_Pct": "Operative Account Rate (%)",
        "Inactive_Pct": "Inactive %"
    },
    height=450
)
fig3.add_hline(y=70, line_dash="dash", line_color="green", annotation_text="70% operative target")
fig3.add_vline(x=50, line_dash="dash", line_color="#1F4E79", annotation_text="50% gender parity")
fig3.update_layout(plot_bgcolor="#F8F9FA", paper_bgcolor="white")
st.plotly_chart(fig3, use_container_width=True)

with st.expander("📖 What does this mean?"):
    st.markdown("""
    - Districts with **higher female share** tend to show **lower operative rates** — suggesting women's accounts are opened but less actively used
    - This points to a deeper issue: **access vs agency** — women have accounts but may face barriers to using them (literacy, permission, distance to bank/ATM)
    - Districts in the **top-right** of the chart (high female % AND high operative %) are genuinely succeeding at women's financial inclusion
    - Policy focus should shift from counting women's accounts to measuring women's transactions
    """)

st.markdown("---")

# ── FULL TABLE ──
st.markdown("### 📋 Complete Karnataka Gender Data")
display = karnataka[["District", "Total_Accounts", "Male_Accounts", "Female_Accounts",
                      "Operative_Accounts", "Male_Pct", "Female_Pct", "Operative_Pct", "Inactive_Pct"]].rename(columns={
    "Total_Accounts": "Total",
    "Male_Accounts": "Male",
    "Female_Accounts": "Female",
    "Operative_Accounts": "Operative",
    "Male_Pct": "Male %",
    "Female_Pct": "Female %",
    "Operative_Pct": "Operative %",
    "Inactive_Pct": "Inactive %"
}).sort_values("Female %", ascending=False).reset_index(drop=True)
display.index = display.index + 1
st.dataframe(display.style.background_gradient(subset=["Female %", "Operative %"], cmap="Greens"), use_container_width=True)

st.download_button("⬇️ Download Karnataka Gender Data", karnataka.to_csv(index=False), "karnataka_gender.csv", "text/csv")

st.markdown("---")
st.markdown("<div class='gov-footer'>🏦 PMJDY Dashboard · Gender data: Rajya Sabha Q2313, 2023 · Ministry of Finance, GoI</div>", unsafe_allow_html=True)
