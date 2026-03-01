import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys, os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.data_loader import load_balance_distribution, load_state_data, load_bihar_districts

st.set_page_config(page_title="Balance Analysis — PMJDY", page_icon="💰", layout="wide")

with open(os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "style.css")) as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

@st.cache_data
def get_data():
    return load_balance_distribution(), load_state_data(), load_bihar_districts()

balance_dist, state_df, bihar = get_data()

with st.sidebar:
    st.markdown("## 💰 Balance Analysis")
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
    <h1 style='margin:0; font-size:24px;'>💰 Balance Analysis — What's Actually in the Accounts?</h1>
    <p style='margin:5px 0 0 0; opacity:0.9;'>The critical question: Are PMJDY accounts holding money, or just sitting empty?</p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class='info-box'>
<b>The activation paradox:</b> India has opened 45+ crore PMJDY accounts — a world record.
But the average balance is just ₹3,703 per account. And most accounts show a disturbing pattern:
money comes in (wages, subsidies) and leaves within days. This section examines the depth of that problem.
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ── KPIs ──
total_deposit = state_df["Deposit_Crore"].sum()
total_accounts = state_df["Accounts"].sum()
avg_balance = total_deposit * 1e7 / total_accounts

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Deposits (National)", f"₹{total_deposit/1e5:.2f} Lakh Cr")
col2.metric("National Avg Balance", f"₹{avg_balance:.0f}", "per account")
col3.metric("Highest State Avg", f"₹{state_df['Avg_Balance_INR'].max():.0f}", state_df.loc[state_df['Avg_Balance_INR'].idxmax(), 'State'])
col4.metric("Lowest State Avg", f"₹{state_df['Avg_Balance_INR'].min():.0f}", state_df.loc[state_df['Avg_Balance_INR'].idxmin(), 'State'])

st.markdown("---")

# ── BALANCE DISTRIBUTION ──
st.markdown("### 📊 How Much Money Do Account Holders Keep?")
st.markdown("*Distribution of average balances across account holders*")
st.markdown("<p class='source-tag'>Source: Rajya Sabha Unstarred Question No. 230, 2024</p>", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    fig = px.pie(
        balance_dist,
        values="Amount_Crore",
        names="Particulars",
        color_discrete_sequence=["#E74C3C", "#F39C12", "#F1C40F", "#2ECC71", "#1F4E79"],
        hole=0.4,
        title="Share of Total Deposits by Balance Slab"
    )
    fig.update_traces(textposition="outside", textinfo="label+percent")
    fig.update_layout(paper_bgcolor="white", height=400, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    fig2 = px.bar(
        balance_dist,
        x="Particulars", y="Amount_Crore",
        color="Amount_Crore",
        color_continuous_scale="Blues",
        text="Amount_Crore",
        labels={"Amount_Crore": "Amount (₹ Crore)", "Particulars": "Balance Slab"},
        title="Deposits by Balance Category (₹ Crore)"
    )
    fig2.update_traces(texttemplate="₹%{text:.2f} Cr", textposition="outside")
    fig2.update_layout(plot_bgcolor="#F8F9FA", paper_bgcolor="white", height=400,
                       xaxis_tickangle=-20, showcoloraxis=False)
    st.plotly_chart(fig2, use_container_width=True)

with st.expander("📖 What does this mean?"):
    st.markdown("""
    - **63% of all PMJDY deposits** come from accounts with less than ₹1,000 balance
    - This means most people are using PMJDY accounts as a **pass-through** — money comes in and goes out quickly
    - Only **4.4%** of deposits come from accounts maintaining more than ₹20,000 — likely salaried urban workers
    - The thin balance distribution is the core challenge: **financial inclusion without financial depth**
    """)

st.markdown("---")

# ── STATE BALANCE COMPARISON ──
st.markdown("### 🗺️ State-wise Average Balance — Who Keeps More?")

col1, col2 = st.columns([3, 1])
with col1:
    fig3 = px.bar(
        state_df.sort_values("Avg_Balance_INR"),
        x="Avg_Balance_INR", y="State",
        orientation="h",
        color="Region",
        labels={"Avg_Balance_INR": "Avg Balance per Account (₹)", "State": ""},
        height=700,
        title=""
    )
    fig3.add_vline(x=avg_balance, line_dash="dash", line_color="#E74C3C",
                   annotation_text=f"National avg: ₹{avg_balance:.0f}")
    fig3.update_layout(plot_bgcolor="#F8F9FA", paper_bgcolor="white")
    st.plotly_chart(fig3, use_container_width=True)

with col2:
    st.markdown("**Key Observations**")
    st.markdown(f"""
    🟢 **Best:** {state_df.loc[state_df['Avg_Balance_INR'].idxmax(), 'State']}
    ₹{state_df['Avg_Balance_INR'].max():,.0f} avg

    🔴 **Needs attention:**
    {state_df.loc[state_df['Avg_Balance_INR'].idxmin(), 'State']}
    ₹{state_df['Avg_Balance_INR'].min():,.0f} avg

    📊 **National avg:**
    ₹{avg_balance:,.0f}

    📌 States **above average** tend to have:
    - More urban population
    - Stronger MGNREGA implementation
    - Better banking infrastructure
    - Higher literacy rates
    """)

st.markdown("---")

# ── BIHAR DISTRICT BALANCE ANALYSIS ──
st.markdown("### 📍 Bihar District Balance — A Deep Dive into India's Poorest State")
st.markdown("<div class='info-box'>Bihar has the most PMJDY accounts (5.1 crore) but among the lowest average balances. This district-level view shows the extreme variation within the state.</div>", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    fig4 = px.bar(
        bihar.sort_values("Avg_Balance_INR"),
        x="Avg_Balance_INR", y="District",
        orientation="h",
        color="Avg_Balance_INR",
        color_continuous_scale="RdYlGn",
        labels={"Avg_Balance_INR": "Avg Balance per Account (₹)", "District": ""},
        height=700
    )
    state_avg = bihar["Avg_Balance_INR"].mean()
    fig4.add_vline(x=state_avg, line_dash="dash", line_color="#1F4E79",
                   annotation_text=f"State avg: ₹{state_avg:.0f}")
    fig4.update_layout(plot_bgcolor="#F8F9FA", paper_bgcolor="white", showcoloraxis=False)
    st.plotly_chart(fig4, use_container_width=True)

with col2:
    st.markdown("**Balance vs Account Size — Is Bigger Better?**")
    fig5 = px.scatter(
        bihar,
        x="Accounts", y="Avg_Balance_INR",
        size="Balance_Crore",
        hover_name="District",
        labels={"Accounts": "Total PMJDY Accounts", "Avg_Balance_INR": "Avg Balance (₹)"},
        height=400
    )
    fig5.update_layout(plot_bgcolor="#F8F9FA", paper_bgcolor="white")
    st.plotly_chart(fig5, use_container_width=True)

    st.markdown("**Top & Bottom 5 Districts by Avg Balance**")
    top5 = bihar.nlargest(5, "Avg_Balance_INR")[["District", "Avg_Balance_INR"]].reset_index(drop=True)
    bot5 = bihar.nsmallest(5, "Avg_Balance_INR")[["District", "Avg_Balance_INR"]].reset_index(drop=True)
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("🟢 Top 5")
        st.dataframe(top5.rename(columns={"Avg_Balance_INR": "Avg Balance (₹)"}), hide_index=True, use_container_width=True)
    with c2:
        st.markdown("🔴 Bottom 5")
        st.dataframe(bot5.rename(columns={"Avg_Balance_INR": "Avg Balance (₹)"}), hide_index=True, use_container_width=True)

st.markdown("---")

# ── GLOBAL CONTEXT ──
st.markdown("### 🌍 India vs Global Financial Inclusion Benchmarks")
global_data = pd.DataFrame({
    "Country": ["India (PMJDY)", "Bangladesh", "Kenya (M-Pesa)", "Brazil", "Mexico", "South Africa", "Nigeria"],
    "Account_Ownership_Pct": [80, 54, 82, 84, 49, 85, 45],
    "Avg_Balance_USD": [44, 38, 120, 210, 85, 180, 52],
    "Type": ["Govt Program", "Mixed", "Mobile Money", "Mixed", "Mixed", "Mixed", "Mixed"]
})

col1, col2 = st.columns(2)
with col1:
    fig6 = px.bar(global_data.sort_values("Account_Ownership_Pct"),
                  x="Account_Ownership_Pct", y="Country", orientation="h",
                  color="Type", title="Account Ownership % — Global Comparison",
                  labels={"Account_Ownership_Pct": "Adults with Bank Account (%)", "Country": ""},
                  height=350)
    fig6.update_layout(plot_bgcolor="#F8F9FA", paper_bgcolor="white")
    st.plotly_chart(fig6, use_container_width=True)

with col2:
    fig7 = px.bar(global_data.sort_values("Avg_Balance_USD"),
                  x="Avg_Balance_USD", y="Country", orientation="h",
                  color="Type", title="Avg Balance (USD) — Global Comparison",
                  labels={"Avg_Balance_USD": "Avg Balance per Account (USD)", "Country": ""},
                  height=350)
    fig7.update_layout(plot_bgcolor="#F8F9FA", paper_bgcolor="white")
    st.plotly_chart(fig7, use_container_width=True)

st.markdown("""
<div class='warning-box'>
<b>Key takeaway:</b> India has achieved world-class account ownership (~80%) through PMJDY.
But average balances remain among the lowest globally — comparable to Nigeria and Bangladesh.
This is the core challenge: <b>financial inclusion achieved, financial depth not yet</b>.
</div>
""", unsafe_allow_html=True)

st.markdown("---")
st.markdown("<div class='gov-footer'>🏦 PMJDY Dashboard · Source: Ministry of Finance, GoI · World Bank Global Findex 2021 · Data: 2024</div>", unsafe_allow_html=True)
