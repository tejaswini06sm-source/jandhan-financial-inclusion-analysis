import streamlit as st
import pandas as pd
import plotly.express as px
import sys, os
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.data_loader import load_state_data

st.set_page_config(page_title="Policy Brief - PMJDY", page_icon="", layout="wide")

try:
    with open(os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "style.css"), encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except:
    pass

@st.cache_data
def get_data():
    return load_state_data()

df = get_data()

# Safe computed values
total_accounts = df['Accounts'].sum()
total_deposit = df['Deposit_Crore'].sum()
avg_balance = (total_deposit * 1e7 / total_accounts) if total_accounts > 0 else 0

# Fill missing Region safely
if 'Region' in df.columns:
    df['Region'] = df['Region'].fillna('Unknown')

#  SIDEBAR 
with st.sidebar:
    st.page_link("app.py", label=" Back to Home")
    st.markdown("---")
    st.markdown("##  Policy Brief")
    st.markdown("---")
    st.markdown("---")
    st.markdown("**Who should read this?**")
    st.markdown(" Policy Researchers")
    st.markdown(" Journalists")
    st.markdown(" Academics")
    st.markdown(" Banking Officials")
    st.markdown(" Government Officers")

#  HEADER 
st.markdown("""
<div class='gov-header'>
    <h1 style='margin:0; font-size:24px;'> Policy Brief - PMJDY Financial Inclusion</h1>
    <p style='margin:5px 0 0 0; opacity:0.9;'>Evidence-based findings and actionable recommendations from real government data</p>
</div>
""", unsafe_allow_html=True)

#  EXECUTIVE SUMMARY 
st.markdown("##  Executive Summary")
st.markdown(f"""
<div style='background:white; padding:25px; border-radius:10px; border:1px solid #DDD; margin-bottom:20px;'>
<p style='font-size:15px; line-height:1.8;'>
India's <b>Pradhan Mantri Jan Dhan Yojana (PMJDY)</b>, launched in August 2014, has achieved a remarkable milestone:
<b>45.8 crore bank accounts</b> opened for previously unbanked citizens, with <b>₹2.31 lakh crore</b> in deposits
as of 2024. This represents one of the world's most ambitious and successful financial inclusion drives,
lifting India's banked population from 53% to over 80% in a decade.
</p>
<p style='font-size:15px; line-height:1.8;'>
<b>However, this dashboard reveals a critical gap:</b> account opening has far outpaced account activation.
Analysis of real data across {len(df)} states and 104 districts shows that average balances remain thin
(national average: <b>₹{avg_balance:,.0f}</b> per account),
indicating that most PMJDY accounts function as <i>pass-through conduits</i> for wages and subsidies
rather than as genuine savings instruments.
</p>
<p style='font-size:15px; line-height:1.8;'>
This analysis identifies <b>three core policy challenges</b> and offers <b>six evidence-based recommendations</b>
to deepen financial inclusion beyond mere account opening.
</p>
</div>
""", unsafe_allow_html=True)

#  3 KEY FINDINGS 
st.markdown("##  Three Core Findings")

col1, col2, col3 = st.columns(3)

with col1:
    st.error("""
    **Finding 1 - The Activation Gap**

    Having an account  using an account.
    Karnataka district data shows 1737% of
    accounts are **inactive** (no transaction
    in 90 days). Nationally, an estimated
    3540% of PMJDY accounts are zero-balance.

    **Root cause:** Accounts were opened in
    government camps without building habits
    of saving. People lack trust, literacy, and
    nearby banking infrastructure to transact.
    """)

with col2:
    st.warning("""
    **Finding 2 - The Cash Dependency Trap**

    Wage earners (MGNREGA, daily labour)
    receive payments via PMJDY but withdraw
    **immediately in cash**. The average
    balance of ₹3,703 nationally suggests
    money stays for days, not months.

    **Root cause:** No incentive to keep money
    in accounts. No interest on small balances.
    No easy digital payment options for
    rural purchases. Cash remains king.
    """)

with col3:
    st.success("""
    **Finding 3 - Geography Determines Fate**

    Avg balance ranges widely across states -
    a large gap between top and bottom states.
    Southern and western states dramatically
    outperform eastern and northeastern states.

    **Root cause:** Banking infrastructure,
    literacy, urbanisation and NREGA
    implementation vary wildly by state.
    A one-size policy cannot fix a
    geographically diverse problem.
    """)

#  EVIDENCE 
st.markdown("---")
st.markdown("##  Evidence Supporting Each Finding")

with st.expander(" Evidence for Finding 1 - Activation Gap", expanded=False):
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Karnataka Avg Inactive Rate", "~27%", "Across 30 districts")
        st.markdown("""
        - Kodagu district: lowest operative rate in Karnataka
        - Chamarajanagar: 30% inactive accounts
        - Urban districts show higher operative rates than rural
        - Source: Rajya Sabha Q2313, 2023
        """)
    with col2:
        try:
            bottom5 = df.nsmallest(5, "Avg_Balance_INR")[["State", "Avg_Balance_INR"]].copy()
            fig = px.bar(bottom5, x="State", y="Avg_Balance_INR",
                         color="Avg_Balance_INR", color_continuous_scale="Reds_r",
                         labels={"Avg_Balance_INR": "Avg Balance (₹)"},
                         title="5 States with Lowest Avg Balance")
            fig.update_layout(plot_bgcolor="#F8F9FA", paper_bgcolor="white", height=300, )
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Chart error: {e}")

with st.expander(" Evidence for Finding 2 - Cash Dependency", expanded=False):
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        **Balance Distribution (National, 2024):**
        - **63%** of all PMJDY deposits come from accounts with < ₹1,000 balance
        - Only **4.4%** of deposits from accounts maintaining > ₹20,000
        - Bihar (5.1 crore accounts) has avg balance of just **₹3,479**
        - Patna (capital city) has highest Bihar balance at ₹4,311
        - Source: Rajya Sabha Q230 & Q246, 2022-2024
        """)
    with col2:
        try:
            balance_data = pd.DataFrame({
                "Category": ["< ₹1,000", "₹1K-5K", "₹5K-10K", "₹10K-20K", "> ₹20K"],
                "Share": [63.1, 22.5, 5.1, 3.5, 4.4]
            })
            fig2 = px.pie(balance_data, values="Share", names="Category",
                          color_discrete_sequence=["#E74C3C", "#F39C12", "#F1C40F", "#2ECC71", "#1F4E79"],
                          title="Distribution of PMJDY Deposits by Balance Slab")
            fig2.update_layout(paper_bgcolor="white", height=300)
            st.plotly_chart(fig2, use_container_width=True)
        except Exception as e:
            st.error(f"Chart error: {e}")

with st.expander(" Evidence for Finding 3 - Geographic Inequality", expanded=False):
    try:
        df_sorted = df.sort_values("Avg_Balance_INR").copy()
        color_col = "Region" if "Region" in df_sorted.columns else None
        fig3 = px.bar(
            df_sorted,
            x="Avg_Balance_INR", y="State",
            orientation="h",
            color=color_col,
            labels={"Avg_Balance_INR": "Avg Balance (₹)", "State": ""},
            height=600,
            title="Avg Balance by State - Geographic Divide is Clear"
        )
        fig3.update_layout(plot_bgcolor="#F8F9FA", paper_bgcolor="white")
        st.plotly_chart(fig3, use_container_width=True)
    except Exception as e:
        st.error(f"Chart error: {e}")

#  RECOMMENDATIONS 
st.markdown("---")
st.markdown("##  Six Evidence-Based Recommendations")

recs = [
    {
        "icon": "1",
        "title": "Shift KPIs from Accounts Opened to Accounts Active",
        "detail": "The government currently measures success by number of accounts opened. This incentivises superficial compliance. Recommended new KPI: % of accounts with at least 4 transactions per quarter. Tie Business Correspondent (BC) agent compensation to active accounts, not opened accounts.",
        "impact": "High", "feasibility": "High", "timeline": "6 months"
    },
    {
        "icon": "2",
        "title": "Mandate 7-Day Balance Float on MGNREGA Wages",
        "detail": "Require all MGNREGA wage payments to PMJDY accounts to maintain a minimum ₹500 balance for 7 days before full withdrawal is permitted. Pair with micro-interest incentive (even 0.5% extra) for maintaining balance. This builds the habit of keeping money in accounts.",
        "impact": "High", "feasibility": "Medium", "timeline": "12 months"
    },
    {
        "icon": "3",
        "title": "Prioritize BC Network in ML-Identified High Priority Districts",
        "detail": "The ML clustering in this dashboard identifies specific states and districts that are underperforming relative to their population. Use this model to guide Business Correspondent network expansion - place new agents in Needs Attention districts first.",
        "impact": "High", "feasibility": "High", "timeline": "12-18 months"
    },
    {
        "icon": "4",
        "title": "Women-Specific Financial Literacy at MGNREGA Worksites",
        "detail": "Karnataka data shows districts with higher female account shares have lower operative rates - suggesting women have accounts but lack agency to use them. Deploy financial literacy camps specifically targeting women at MGNREGA worksites, Anganwadi centres, and SHG meetings.",
        "impact": "Medium", "feasibility": "High", "timeline": "6 months"
    },
    {
        "icon": "5",
        "title": "Interoperable Rural Digital Payment Infrastructure",
        "detail": "People withdraw cash because there's nowhere rural to spend digitally. Expand UPI QR code acceptance among kirana stores, vegetable vendors and transport in districts with low operative rates. Subsidize POS terminals for rural merchants in High Priority districts.",
        "impact": "High", "feasibility": "Medium", "timeline": "18-24 months"
    },
    {
        "icon": "6",
        "title": "State-Specific Strategies - One Policy Can't Fit All",
        "detail": "There is a large gap between top and bottom performing states. These states need fundamentally different approaches. Southern states need activation strategies. Eastern states need infrastructure. Northeastern states need mobile banking solutions adapted to terrain.",
        "impact": "High", "feasibility": "Medium", "timeline": "Ongoing"
    }
]

for i, rec in enumerate(recs):
    with st.expander(f"{rec['icon']} {rec['title']}", expanded=(i == 0)):
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(rec["detail"])
        with col2:
            st.markdown(f"**Impact:** {rec['impact']}")
            st.markdown(f"**Feasibility:** {rec['feasibility']}")
            st.markdown(f"**Timeline:** {rec['timeline']}")

#  DOWNLOAD 
st.markdown("---")
st.markdown("##  Download Policy Brief")

policy_text = f"""
PMJDY FINANCIAL INCLUSION - POLICY BRIEF
Generated: {datetime.now().strftime('%B %Y')}
Data: Ministry of Finance, GoI (Rajya Sabha Questions, 2022-2024)

EXECUTIVE SUMMARY
=================
India's PMJDY has opened 45.8 crore accounts with ₹2.31 lakh crore in deposits (2024).
However, the national average balance is just ₹{avg_balance:,.0f} per account,
indicating most accounts are pass-through rather than genuine savings.

THREE CORE FINDINGS
===================
1. THE ACTIVATION GAP: ~35-40% of PMJDY accounts are inactive or zero-balance
2. CASH DEPENDENCY: 63% of all deposits come from accounts with < Rs.1,000 balance
3. GEOGRAPHIC INEQUALITY: Large gap in avg balance between best and worst performing states

SIX RECOMMENDATIONS
===================
1. Shift KPIs from accounts opened to accounts active
2. Mandate 7-day balance float on MGNREGA wages
3. Prioritize BC network in ML-identified high-priority districts
4. Women-specific financial literacy at MGNREGA worksites
5. Interoperable rural digital payment infrastructure
6. State-specific strategies - one policy cannot fit all

DATA SOURCES
============
- Rajya Sabha Unstarred Question No. 230 (2024) - Balance distribution
- Rajya Sabha Unstarred Question No. 239 (2024) - State-wise accounts
- Rajya Sabha Unstarred Question No. 246 (2022) - Bihar district data
- Rajya Sabha Unstarred Question No. 2313 (2023) - Karnataka district data
- Rajya Sabha Unstarred Question No. 886 (2024) - Maharashtra district data
- pmjdy.gov.in - National statistics
"""

col1, col2 = st.columns(2)
with col1:
    st.download_button(
        " Download Policy Brief (TXT)",
        policy_text,
        f"pmjdy_policy_brief_{datetime.now().strftime('%Y%m')}.txt",
        "text/plain"
    )
with col2:
    csv_data = df.to_csv(index=False)
    st.download_button(
        " Download Full Dataset (CSV)",
        csv_data,
        "pmjdy_complete_dataset.csv",
        "text/csv"
    )

#  SOURCES 
st.markdown("---")
st.markdown("###  Official Sources")
st.markdown("""
| Document | Source | Year |
|----------|--------|------|
| PMJDY Progress Report | pmjdy.gov.in | 2024 |
| RS Q230 - Balance Distribution | Ministry of Finance, Rajya Sabha | 2024 |
| RS Q239 - State-wise Accounts | Ministry of Finance, Rajya Sabha | 2024 |
| RS Q246 - Bihar Districts | Ministry of Finance, Rajya Sabha | 2022 |
| RS Q2313 - Karnataka Districts | Ministry of Finance, Rajya Sabha | 2023 |
| RS Q886 - Maharashtra Districts | Ministry of Finance, Rajya Sabha | 2024 |
| World Bank Global Findex | World Bank | 2021 |
""")
st.markdown("---")
st.markdown("<div class='gov-footer'> PMJDY Dashboard  Policy analysis based on real government data  Not affiliated with GoI  2024</div>", unsafe_allow_html=True)