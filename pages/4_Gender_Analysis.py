import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys, os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.data_loader import load_karnataka_districts, load_state_data

st.set_page_config(page_title="Gender Analysis — PMJDY", page_icon="👥", layout="wide")

with open(os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "style.css"), encoding="utf-8") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

@st.cache_data
def get_data():
    return load_karnataka_districts(), load_state_data()

karnataka, state_df = get_data()

with st.sidebar:
    st.page_link("app.py", label="🏠 Back to Home")
    st.markdown("---")
    st.markdown("## 👥 Gender Analysis")
    st.markdown("---")
    st.markdown("---")
    st.markdown("### 🔽 Filters")
    district_search = st.text_input("🔍 Search District", placeholder="Type district name...")
    female_range = st.slider("Female % range:", 0, 100, (0, 100))
    operative_range = st.slider("Operative % range:", 0, 100, (0, 100))
    top_n = st.slider("Top N districts in charts:", 5, 30, 15, 5)
    sort_gender_by = st.selectbox("Sort gender chart by:", ["Female_Pct", "Operative_Pct", "Total_Accounts", "Inactive_Pct"],
        format_func=lambda x: {"Female_Pct": "Female %", "Operative_Pct": "Operative %", "Total_Accounts": "Total Accounts", "Inactive_Pct": "Inactive %"}[x])
    sort_dir = st.radio("Sort order:", ["Ascending", "Descending"], horizontal=True)
    st.markdown("---")
    st.markdown("<div class='info-box'><small>Gender data: Karnataka 30 districts (2023)</small></div>", unsafe_allow_html=True)

st.markdown("""
<div class='gov-header'>
    <h1 style='margin:0; font-size:24px;'>👥 Gender Analysis — Female Financial Inclusion</h1>
    <p style='margin:5px 0 0 0; opacity:0.9;'>Who holds PMJDY accounts? Are women being left behind?</p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class='info-box'>
<b>Why gender matters:</b> PMJDY was explicitly designed to prioritize women. But access ≠ usage.
This section examines whether women are truly included or just counted.
<br><b>Data:</b> Karnataka district-level gender breakdown (30 districts, 2023)
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ── NATIONAL CONTEXT ──
st.markdown("### 🌍 National Gender Picture")
total_accounts = 458932822
women_accounts = 248500000
men_accounts = total_accounts - women_accounts

col1, col2, col3 = st.columns(3)
col1.metric("Women Account Holders", f"{women_accounts/1e7:.1f} Cr", "~54% of all accounts")
col2.metric("Men Account Holders", f"{men_accounts/1e7:.1f} Cr", "~46% of all accounts")
col3.metric("Women's Share", "54.2%", "Exceeds 50% — positive sign")

fig_donut = go.Figure(data=[go.Pie(
    labels=["Women", "Men"], values=[women_accounts, men_accounts],
    hole=0.5, marker_colors=["#E84393", "#1F4E79"], textinfo="label+percent"
)])
fig_donut.update_layout(title="National Gender Split — PMJDY Account Holders", paper_bgcolor="white", height=320,
    annotations=[dict(text="45.8 Cr<br>Total", x=0.5, y=0.5, font_size=14, showarrow=False)])
st.plotly_chart(fig_donut, use_container_width=True)

st.markdown("---")

# ── APPLY FILTERS ──
df = karnataka.copy()
if district_search:
    df = df[df["District"].str.contains(district_search, case=False, na=False)]
df = df[df["Female_Pct"].between(female_range[0], female_range[1])]
df = df[df["Operative_Pct"].between(operative_range[0], operative_range[1])]

# Active filter display
active = []
if district_search: active.append(f"Search: '{district_search}'")
if female_range != (0, 100): active.append(f"Female %: {female_range[0]}–{female_range[1]}")
if operative_range != (0, 100): active.append(f"Operative %: {operative_range[0]}–{operative_range[1]}")
if active:
    st.markdown(f"<div class='info-box'>🔽 <b>Active filters:</b> {' · '.join(active)} — showing <b>{len(df)}</b> of <b>{len(karnataka)}</b> districts</div>", unsafe_allow_html=True)

st.markdown(f"### 📍 Karnataka District Gender Analysis — {len(df)} Districts")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Accounts", f"{df['Total_Accounts'].sum()/1e5:.0f} Lakh")
col2.metric("Female Accounts", f"{df['Female_Accounts'].sum()/1e5:.0f} Lakh")
col3.metric("Male Accounts", f"{df['Male_Accounts'].sum()/1e5:.0f} Lakh")
col4.metric("Avg Female %", f"{(df['Female_Accounts'].sum()/df['Total_Accounts'].sum()*100):.1f}%")

asc = (sort_dir == "Ascending")

col1, col2 = st.columns(2)
with col1:
    st.markdown("**Female Account Share by District (%)**")
    chart_df = df.sort_values(sort_gender_by, ascending=asc)
    fig = px.bar(chart_df, x="Female_Pct", y="District", orientation="h",
                 color="Female_Pct", color_continuous_scale="RdYlGn", range_color=[40, 60],
                 labels={"Female_Pct": "Female Accounts (%)", "District": ""}, height=550)
    fig.add_vline(x=50, line_dash="dash", line_color="#1F4E79", annotation_text="50% parity")
    fig.update_layout(plot_bgcolor="#F8F9FA", paper_bgcolor="white")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown(f"**Male vs Female — Top {top_n} Districts by Total Accounts**")
    top15 = df.nlargest(top_n, "Total_Accounts").sort_values("Total_Accounts", ascending=asc)
    fig2 = go.Figure()
    fig2.add_trace(go.Bar(name="Female", y=top15["District"], x=top15["Female_Accounts"], orientation="h", marker_color="#E84393"))
    fig2.add_trace(go.Bar(name="Male", y=top15["District"], x=top15["Male_Accounts"], orientation="h", marker_color="#1F4E79"))
    fig2.update_layout(barmode="group", height=550, plot_bgcolor="#F8F9FA", paper_bgcolor="white", xaxis_title="Number of Accounts")
    st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")
st.markdown("### 🔄 Female Share vs Operative Rate — Access vs Agency")
st.markdown("<div class='info-box'>Do districts with more women's accounts have more or less active usage?</div>", unsafe_allow_html=True)

color_scatter = st.radio("Color scatter by:", ["Inactive_Pct", "Operative_Pct", "Total_Accounts"], horizontal=True,
                          format_func=lambda x: {"Inactive_Pct": "Inactive %", "Operative_Pct": "Operative %", "Total_Accounts": "Total Accounts"}[x])

fig3 = px.scatter(df, x="Female_Pct", y="Operative_Pct", size="Total_Accounts", hover_name="District",
                   color=color_scatter,
                   color_continuous_scale="RdYlGn" if "Pct" in color_scatter else "Blues",
                   labels={"Female_Pct": "Female Account Share (%)", "Operative_Pct": "Operative Account Rate (%)"}, height=450)
fig3.add_hline(y=70, line_dash="dash", line_color="green", annotation_text="70% operative target")
fig3.add_vline(x=50, line_dash="dash", line_color="#1F4E79", annotation_text="50% gender parity")
fig3.update_layout(plot_bgcolor="#F8F9FA", paper_bgcolor="white")
st.plotly_chart(fig3, use_container_width=True)

st.markdown("---")
st.markdown("### 📋 Complete Karnataka Gender Data")

table_sort = st.selectbox("Sort table by:", ["Female %", "Operative %", "Inactive %", "Total"],
    index=0)
sort_col_map = {"Female %": "Female_Pct", "Operative %": "Operative_Pct", "Inactive %": "Inactive_Pct", "Total": "Total_Accounts"}

display = df[["District", "Total_Accounts", "Male_Accounts", "Female_Accounts",
              "Operative_Accounts", "Male_Pct", "Female_Pct", "Operative_Pct", "Inactive_Pct"]].rename(columns={
    "Total_Accounts": "Total", "Male_Accounts": "Male", "Female_Accounts": "Female",
    "Operative_Accounts": "Operative", "Male_Pct": "Male %", "Female_Pct": "Female %",
    "Operative_Pct": "Operative %", "Inactive_Pct": "Inactive %"
}).sort_values(table_sort, ascending=asc).reset_index(drop=True)
display.index = display.index + 1
st.dataframe(display.style.background_gradient(subset=["Female %", "Operative %"], cmap="Greens"), use_container_width=True)
st.download_button("⬇️ Download Karnataka Gender Data", karnataka.to_csv(index=False), "karnataka_gender.csv", "text/csv")

st.markdown("---")
st.markdown("<div class='gov-footer'>🏦 PMJDY Dashboard · Gender data: Rajya Sabha Q2313, 2023 · Ministry of Finance, GoI</div>", unsafe_allow_html=True)