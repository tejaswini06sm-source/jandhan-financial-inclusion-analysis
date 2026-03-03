import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys, os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.data_loader import load_balance_distribution, load_state_data, load_bihar_districts

st.set_page_config(page_title="Balance Analysis - PMJDY", page_icon="💰", layout="wide")

with open(os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "style.css"), encoding="utf-8") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

@st.cache_data
def get_data():
    return load_balance_distribution(), load_state_data(), load_bihar_districts()

balance_dist, state_df, bihar = get_data()

with st.sidebar:
    st.page_link("app.py", label="🏠 Back to Home")
    st.markdown("---")
    st.markdown("## 💰 Balance Analysis")
    st.markdown("---")
    st.markdown("---")
    st.markdown("### 🔽 Filters")

    # Region filter for state chart
    regions = sorted(state_df["Region"].dropna().unique())
    region_filter = st.multiselect("🌏 Filter States by Region", regions, default=regions)

    # Balance range filter for state chart
    bal_min = int(state_df["Avg_Balance_INR"].min())
    bal_max = int(state_df["Avg_Balance_INR"].max())
    bal_range = st.slider("💰 State Avg Balance Range (₹)", bal_min, bal_max, (bal_min, bal_max), step=100)

    # Bihar filters
    st.markdown("---")
    st.markdown("**Bihar District Filters**")
    bihar_search = st.text_input("🔍 Search Bihar District", placeholder="Type district name...")
    bihar_bal_min = int(bihar["Avg_Balance_INR"].min())
    bihar_bal_max = int(bihar["Avg_Balance_INR"].max())
    bihar_bal_range = st.slider("Bihar Balance Range (₹)", bihar_bal_min, bihar_bal_max, (bihar_bal_min, bihar_bal_max), step=50)
    top_n_bihar = st.slider("Top N Bihar districts:", 5, 38, 38, 5)

    # Chart options
    st.markdown("---")
    st.markdown("**Chart Options**")
    state_sort = st.radio("Sort state chart by:", ["Avg_Balance_INR", "Deposit_Crore"], horizontal=True,
                           format_func=lambda x: {"Avg_Balance_INR": "Avg Balance", "Deposit_Crore": "Total Deposits"}[x])
    show_nat_avg_line = st.checkbox("Show national avg line", value=True)

# ── APPLY FILTERS ──
filtered_states = state_df[
    state_df["Region"].isin(region_filter) &
    state_df["Avg_Balance_INR"].between(bal_range[0], bal_range[1])
]

filtered_bihar = bihar.copy()
if bihar_search:
    filtered_bihar = filtered_bihar[filtered_bihar["District"].str.contains(bihar_search, case=False, na=False)]
filtered_bihar = filtered_bihar[filtered_bihar["Avg_Balance_INR"].between(bihar_bal_range[0], bihar_bal_range[1])]

st.markdown("""
<div class='gov-header'>
    <h1 style='margin:0; font-size:24px;'>💰 Balance Analysis - What's Actually in the Accounts?</h1>
    <p style='margin:5px 0 0 0; opacity:0.9;'>Are PMJDY accounts holding money, or just sitting empty?</p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div style='background:#FFFFFF;border-left:4px solid #2563B0;border-radius:6px;padding:10px 14px;font-size:13px;color:#1E293B;line-height:1.6;'>
<b>The activation paradox:</b> India has opened 45+ crore PMJDY accounts. But the average balance is just ₹3,703.
Money comes in (wages, subsidies) and leaves within days. This section examines the depth of that problem.
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ── KPIs ──
total_deposit = filtered_states["Deposit_Crore"].sum()
total_accounts = filtered_states["Accounts"].sum()
avg_balance = total_deposit * 1e7 / total_accounts if total_accounts > 0 else 0

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("States Shown", len(filtered_states), f"of {len(state_df)}")
col2.metric("Total Deposits", f"₹{total_deposit/1e5:.2f} Lakh Cr")
col3.metric("Avg Balance (Filtered)", f"₹{avg_balance:.0f}")
col4.metric("Highest State", f"₹{filtered_states['Avg_Balance_INR'].max():.0f}", filtered_states.loc[filtered_states['Avg_Balance_INR'].idxmax(), 'State'])
col5.metric("Lowest State", f"₹{filtered_states['Avg_Balance_INR'].min():.0f}", filtered_states.loc[filtered_states['Avg_Balance_INR'].idxmin(), 'State'])

# Active filter summary
active = []
if len(region_filter) < len(regions): active.append(f"Regions: {', '.join(region_filter)}")
if bal_range != (bal_min, bal_max): active.append(f"Balance: ₹{bal_range[0]:,}–₹{bal_range[1]:,}")
if active:
    st.markdown(f"<div style='background:#FFFFFF;border-left:4px solid #2563B0;border-radius:6px;padding:10px 14px;font-size:13px;color:#1E293B;line-height:1.6;'>🔽 <b>Active filters:</b> {' · '.join(active)}</div>", unsafe_allow_html=True)

st.markdown("---")

# ── BALANCE DISTRIBUTION ──
st.markdown("### 📊 Balance Slab Distribution - National")
st.markdown("<p class='source-tag'>Source: Rajya Sabha Unstarred Question No. 230, 2024</p>", unsafe_allow_html=True)

slab_filter = st.multiselect("Filter slabs:", balance_dist["Particulars"].tolist(), default=balance_dist["Particulars"].tolist())
bal_dist_filtered = balance_dist[balance_dist["Particulars"].isin(slab_filter)]

col1, col2 = st.columns(2)
with col1:
    fig = px.pie(bal_dist_filtered, values="Amount_Crore", names="Particulars",
                 color_discrete_sequence=["#E74C3C", "#F39C12", "#F1C40F", "#2ECC71", "#1F4E79"],
                 hole=0.4, title="Share of Total Deposits by Balance Slab")
    fig.update_traces(textposition="outside", textinfo="label+percent")
    fig.update_layout(paper_bgcolor="white", height=380, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    fig2 = px.bar(bal_dist_filtered, x="Particulars", y="Amount_Crore",
                  color="Amount_Crore", color_continuous_scale="Blues", text="Amount_Crore",
                  labels={"Amount_Crore": "Amount (₹ Crore)", "Particulars": "Balance Slab"},
                  title="Deposits by Balance Category (₹ Crore)")
    fig2.update_traces(texttemplate="₹%{text:.2f} Cr", textposition="outside")
    fig2.update_layout(plot_bgcolor="#F8F9FA", paper_bgcolor="white", height=380, xaxis_tickangle=-20, )
    st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")

# ── STATE BALANCE COMPARISON ──
st.markdown(f"### 🗺️ State-wise Avg Balance - {len(filtered_states)} States")

nat_avg = state_df["Deposit_Crore"].sum() * 1e7 / state_df["Accounts"].sum()
color_state_by = st.radio("Color state chart by:", ["Region", "Tier"] if "Tier" in filtered_states.columns else ["Region"], horizontal=True)

col1, col2 = st.columns([3, 1])
with col1:
    fig3 = px.bar(filtered_states.sort_values(state_sort), x=state_sort, y="State", orientation="h",
                  color=color_state_by,
                  labels={state_sort: "Avg Balance per Account (₹)" if state_sort == "Avg_Balance_INR" else "Total Deposits (Cr)", "State": ""},
                  height=max(400, len(filtered_states) * 20))
    if show_nat_avg_line:
        fig3.add_vline(x=nat_avg if state_sort == "Avg_Balance_INR" else state_df["Deposit_Crore"].mean(),
                       line_dash="dash", line_color="#E74C3C",
                       annotation_text=f"National avg: ₹{nat_avg:.0f}" if state_sort == "Avg_Balance_INR" else "Avg deposits")
    fig3.update_layout(plot_bgcolor="#F8F9FA", paper_bgcolor="white", coloraxis_showscale=False)
    st.plotly_chart(fig3, use_container_width=True)

with col2:
    st.markdown("**Key Stats**")
    st.markdown(f"🟢 **Best:** {filtered_states.loc[filtered_states['Avg_Balance_INR'].idxmax(), 'State']} - ₹{filtered_states['Avg_Balance_INR'].max():,.0f}")
    st.markdown(f"🔴 **Lowest:** {filtered_states.loc[filtered_states['Avg_Balance_INR'].idxmin(), 'State']} - ₹{filtered_states['Avg_Balance_INR'].min():,.0f}")
    st.markdown(f"📊 **Filtered avg:** ₹{filtered_states['Avg_Balance_INR'].mean():,.0f}")
    st.markdown(f"📊 **National avg:** ₹{nat_avg:,.0f}")
    spread = filtered_states['Avg_Balance_INR'].max() / filtered_states['Avg_Balance_INR'].min()
    st.markdown(f"📐 **Gap (max/min):** {spread:.1f}x")

st.markdown("---")

# ── BIHAR DISTRICT BALANCE ──
st.markdown(f"### 📍 Bihar District Balance - {len(filtered_bihar)} Districts")
st.markdown("<div style='background:#FFFFFF;border-left:4px solid #2563B0;border-radius:6px;padding:10px 14px;font-size:13px;color:#1E293B;line-height:1.6;'>Bihar has the most PMJDY accounts but among the lowest balances. District-level view shows extreme variation within the state.</div>", unsafe_allow_html=True)

bihar_sort = st.radio("Sort Bihar chart by:", ["Avg_Balance_INR", "Accounts", "Balance_Crore"], horizontal=True,
                       format_func=lambda x: {"Avg_Balance_INR": "Avg Balance", "Accounts": "Total Accounts", "Balance_Crore": "Total Balance"}[x])

col1, col2 = st.columns(2)
with col1:
    top_bihar = filtered_bihar.nlargest(top_n_bihar, bihar_sort).sort_values(bihar_sort)
    fig4 = px.bar(top_bihar, x=bihar_sort, y="District", orientation="h",
                  color="Avg_Balance_INR", color_continuous_scale="RdYlGn",
                  labels={"Avg_Balance_INR": "Avg Balance (₹)", "District": ""}, height=600)
    bihar_avg = filtered_bihar["Avg_Balance_INR"].mean()
    if show_nat_avg_line and bihar_sort == "Avg_Balance_INR":
        fig4.add_vline(x=bihar_avg, line_dash="dash", line_color="#1F4E79", annotation_text=f"State avg: ₹{bihar_avg:.0f}")
    fig4.update_layout(plot_bgcolor="#F8F9FA", paper_bgcolor="white", )
    st.plotly_chart(fig4, use_container_width=True)

with col2:
    st.markdown("**Balance vs Account Size**")
    fig5 = px.scatter(filtered_bihar, x="Accounts", y="Avg_Balance_INR", size="Balance_Crore",
                      hover_name="District", labels={"Accounts": "Total PMJDY Accounts", "Avg_Balance_INR": "Avg Balance (₹)"}, height=350)
    fig5.update_layout(plot_bgcolor="#F8F9FA", paper_bgcolor="white")
    st.plotly_chart(fig5, use_container_width=True)
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("🟢 **Top 5**")
        st.dataframe(filtered_bihar.nlargest(5, "Avg_Balance_INR")[["District", "Avg_Balance_INR"]].rename(columns={"Avg_Balance_INR": "Avg Balance (₹)"}).reset_index(drop=True), hide_index=True, use_container_width=True)
    with c2:
        st.markdown("🔴 **Bottom 5**")
        st.dataframe(filtered_bihar.nsmallest(5, "Avg_Balance_INR")[["District", "Avg_Balance_INR"]].rename(columns={"Avg_Balance_INR": "Avg Balance (₹)"}).reset_index(drop=True), hide_index=True, use_container_width=True)

st.markdown("---")

# ── GLOBAL CONTEXT ──
st.markdown("### 🌍 India vs Global Benchmarks")
global_data = pd.DataFrame({
    "Country": ["India (PMJDY)", "Bangladesh", "Kenya (M-Pesa)", "Brazil", "Mexico", "South Africa", "Nigeria"],
    "Account_Ownership_Pct": [80, 54, 82, 84, 49, 85, 45],
    "Avg_Balance_USD": [44, 38, 120, 210, 85, 180, 52],
    "Type": ["Govt Program", "Mixed", "Mobile Money", "Mixed", "Mixed", "Mixed", "Mixed"]
})
highlight_india = st.checkbox("Highlight India", value=True)
col1, col2 = st.columns(2)
with col1:
    fig6 = px.bar(global_data.sort_values("Account_Ownership_Pct"), x="Account_Ownership_Pct", y="Country",
                  orientation="h", color="Type", title="Account Ownership % - Global",
                  labels={"Account_Ownership_Pct": "Adults with Bank Account (%)", "Country": ""}, height=330)
    fig6.update_layout(plot_bgcolor="#F8F9FA", paper_bgcolor="white")
    st.plotly_chart(fig6, use_container_width=True)
with col2:
    fig7 = px.bar(global_data.sort_values("Avg_Balance_USD"), x="Avg_Balance_USD", y="Country",
                  orientation="h", color="Type", title="Avg Balance (USD) - Global",
                  labels={"Avg_Balance_USD": "Avg Balance per Account (USD)", "Country": ""}, height=330)
    fig7.update_layout(plot_bgcolor="#F8F9FA", paper_bgcolor="white")
    st.plotly_chart(fig7, use_container_width=True)

st.markdown("""
<div class='warning-box'>
<b>Key takeaway:</b> India has achieved world-class account ownership (~80%) through PMJDY.
But average balances remain among the lowest globally. <b>Financial inclusion achieved, financial depth not yet.</b>
</div>
""", unsafe_allow_html=True)

st.markdown("---")
col1, col2 = st.columns(2)
with col1:
    st.download_button("⬇️ Download Filtered State Data", filtered_states.to_csv(index=False), "pmjdy_balance_states.csv", "text/csv")
with col2:
    st.download_button("⬇️ Download Filtered Bihar Data", filtered_bihar.to_csv(index=False), "pmjdy_balance_bihar.csv", "text/csv")

st.markdown("---")
st.markdown("<div class='gov-footer'>🏦 PMJDY Dashboard · Source: Ministry of Finance, GoI · World Bank Global Findex 2021 · Data: 2024</div>", unsafe_allow_html=True)