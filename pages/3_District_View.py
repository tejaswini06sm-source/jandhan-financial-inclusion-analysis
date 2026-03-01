import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys, os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.data_loader import load_bihar_districts, load_karnataka_districts, load_maharashtra_districts
from utils.ml_models import detect_anomalies

st.set_page_config(page_title="District Explorer — PMJDY", page_icon="🏘️", layout="wide")

with open(os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "style.css")) as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

@st.cache_data
def get_data():
    bihar = load_bihar_districts()
    karnataka = load_karnataka_districts()
    maharashtra = load_maharashtra_districts()
    return bihar, karnataka, maharashtra

bihar, karnataka, maharashtra = get_data()

with st.sidebar:
    st.markdown("## 🏘️ District Explorer")
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
    selected_state = st.radio("Select State", ["Bihar", "Karnataka", "Maharashtra"])
    st.markdown("---")
    st.markdown("<div class='info-box'><small>District data available for Bihar (38), Karnataka (30), and Maharashtra (36) from official government sources.</small></div>", unsafe_allow_html=True)

st.markdown("""
<div class='gov-header'>
    <h1 style='margin:0; font-size:24px;'>🏘️ District Explorer</h1>
    <p style='margin:5px 0 0 0; opacity:0.9;'>Search, compare and analyse districts — Bihar · Karnataka · Maharashtra</p>
</div>
""", unsafe_allow_html=True)

# ── SELECT STATE DATA ──
if selected_state == "Bihar":
    df = bihar.copy()
    df = detect_anomalies(df, "Accounts", "Balance_Crore")
    st.markdown("### 📍 Bihar — 38 Districts")
    st.markdown("<div class='info-box'>Data: Rajya Sabha Unstarred Question No. 246, 2022. Shows total PMJDY accounts and balance held per district.</div>", unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Districts", 38)
    col2.metric("Total Accounts", f"{df['Accounts'].sum()/1e5:.0f} Lakh")
    col3.metric("Total Balance", f"₹{df['Balance_Crore'].sum():.0f} Cr")
    col4.metric("Avg Balance/Account", f"₹{df['Avg_Balance_INR'].mean():.0f}")

    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Top 10 Districts by Accounts**")
        fig = px.bar(df.nlargest(10, "Accounts").sort_values("Accounts"),
                     x="Accounts", y="District", orientation="h",
                     color="Avg_Balance_INR", color_continuous_scale="Blues",
                     labels={"Accounts": "Total PMJDY Accounts", "Avg_Balance_INR": "Avg Balance (₹)"},
                     height=400)
        fig.update_layout(plot_bgcolor="#F8F9FA", paper_bgcolor="white")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("**Accounts vs Balance — District Scatter**")
        fig2 = px.scatter(df, x="Accounts", y="Avg_Balance_INR",
                          hover_name="District", size="Accounts",
                          color="Anomaly_Type",
                          color_discrete_map={"Normal": "#2A9D8F", "Unusually High": "#E76F51", "Unusually Low": "#F4A261"},
                          labels={"Accounts": "Total Accounts", "Avg_Balance_INR": "Avg Balance (₹)"},
                          height=400)
        fig2.update_layout(plot_bgcolor="#F8F9FA", paper_bgcolor="white")
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("**📋 Full Bihar District Data**")
    display = df[["District", "Accounts", "Accounts_Lakh", "Balance_Crore", "Avg_Balance_INR", "Anomaly_Type"]].rename(columns={
        "Accounts_Lakh": "Accounts (Lakh)",
        "Balance_Crore": "Balance (Cr)",
        "Avg_Balance_INR": "Avg Balance (₹)",
        "Anomaly_Type": "Pattern"
    }).sort_values("Avg Balance (₹)", ascending=False).reset_index(drop=True)
    display.index = display.index + 1
    st.dataframe(display.style.background_gradient(subset=["Avg Balance (₹)"], cmap="Greens"), use_container_width=True)
    st.download_button("⬇️ Download Bihar Data", df.to_csv(index=False), "bihar_districts.csv", "text/csv")

elif selected_state == "Karnataka":
    df = karnataka.copy()
    df = detect_anomalies(df, "Total_Accounts")
    st.markdown("### 📍 Karnataka — 30 Districts")
    st.markdown("<div class='info-box'>Data: Rajya Sabha Unstarred Question No. 2313, 2023. Shows total, male, female, and operative PMJDY accounts per district.</div>", unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Districts", 30)
    col2.metric("Total Accounts", f"{df['Total_Accounts'].sum()/1e5:.0f} Lakh")
    col3.metric("Avg Operative %", f"{df['Operative_Pct'].mean():.1f}%")
    col4.metric("Avg Female %", f"{df['Female_Pct'].mean():.1f}%")

    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Operative vs Inactive Accounts by District**")
        fig = go.Figure()
        df_sorted = df.sort_values("Operative_Pct", ascending=True)
        fig.add_trace(go.Bar(name="Operative", y=df_sorted["District"], x=df_sorted["Operative_Accounts"],
                             orientation="h", marker_color="#2A9D8F"))
        fig.add_trace(go.Bar(name="Inactive", y=df_sorted["District"], x=df_sorted["Inactive_Accounts"],
                             orientation="h", marker_color="#E76F51"))
        fig.update_layout(barmode="stack", height=600, plot_bgcolor="#F8F9FA",
                          paper_bgcolor="white", xaxis_title="Number of Accounts")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("**Female Account Share by District**")
        fig2 = px.bar(df.sort_values("Female_Pct"),
                      x="Female_Pct", y="District", orientation="h",
                      color="Female_Pct", color_continuous_scale="RdYlGn",
                      labels={"Female_Pct": "Female Accounts (%)", "District": ""},
                      height=600)
        fig2.add_vline(x=50, line_dash="dash", line_color="#1F4E79", annotation_text="50% parity line")
        fig2.update_layout(plot_bgcolor="#F8F9FA", paper_bgcolor="white")
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("**📋 Full Karnataka District Data**")
    display = df[["District", "Total_Accounts", "Male_Accounts", "Female_Accounts", "Operative_Accounts", "Female_Pct", "Operative_Pct", "Inactive_Pct"]].rename(columns={
        "Total_Accounts": "Total",
        "Male_Accounts": "Male",
        "Female_Accounts": "Female",
        "Operative_Accounts": "Operative",
        "Female_Pct": "Female %",
        "Operative_Pct": "Operative %",
        "Inactive_Pct": "Inactive %"
    }).sort_values("Operative %", ascending=False).reset_index(drop=True)
    display.index = display.index + 1
    st.dataframe(display.style.background_gradient(subset=["Operative %"], cmap="Greens"), use_container_width=True)
    st.download_button("⬇️ Download Karnataka Data", df.to_csv(index=False), "karnataka_districts.csv", "text/csv")

elif selected_state == "Maharashtra":
    df = maharashtra.copy()
    st.markdown("### 📍 Maharashtra — 36 Districts (2022–2024 Trend)")
    st.markdown("<div class='info-box'>Data: Rajya Sabha Unstarred Question No. 886, 2024. Unique 4-point time series — March 2022, March 2023, March 2024, June 2024.</div>", unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Districts", 36)
    col2.metric("Accounts (Jun 2024)", f"{df['Jun_2024'].sum()/1e5:.0f} Lakh")
    col3.metric("Avg 2yr Growth", f"{df['Growth_2022_2024'].mean():.1f}%")
    col4.metric("Fastest Growing", df.loc[df["Growth_2022_2024"].idxmax(), "District"])

    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**2-Year Account Growth by District (2022→2024)**")
        fig = px.bar(df.sort_values("Growth_2022_2024"),
                     x="Growth_2022_2024", y="District", orientation="h",
                     color="Growth_2022_2024",
                     color_continuous_scale="RdYlGn",
                     labels={"Growth_2022_2024": "Growth % (2022→2024)", "District": ""},
                     height=600)
        fig.update_layout(plot_bgcolor="#F8F9FA", paper_bgcolor="white")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("**Select a District — 4-Year Trend**")
        selected_district = st.selectbox("Choose District", sorted(df["District"].tolist()))
        row = df[df["District"] == selected_district].iloc[0]
        trend_data = pd.DataFrame({
            "Period": ["Mar 2022", "Mar 2023", "Mar 2024", "Jun 2024"],
            "Accounts": [row["Mar_2022"], row["Mar_2023"], row["Mar_2024"], row["Jun_2024"]]
        }).dropna()
        fig2 = px.line(trend_data, x="Period", y="Accounts",
                       markers=True, title=f"{selected_district} — Account Growth Trend",
                       labels={"Accounts": "PMJDY Accounts", "Period": ""},
                       height=350)
        fig2.update_traces(line_color="#1F4E79", marker_size=10)
        fig2.update_layout(plot_bgcolor="#F8F9FA", paper_bgcolor="white")
        st.plotly_chart(fig2, use_container_width=True)

        if pd.notna(row["Growth_2022_2024"]):
            st.metric("2-Year Growth", f"{row['Growth_2022_2024']:.1f}%",
                      "vs state avg " + f"{df['Growth_2022_2024'].mean():.1f}%")

    st.markdown("**📋 Full Maharashtra District Data**")
    display = df[["District", "Mar_2022", "Mar_2023", "Mar_2024", "Jun_2024", "Growth_2022_2024"]].rename(columns={
        "Mar_2022": "Mar 2022",
        "Mar_2023": "Mar 2023",
        "Mar_2024": "Mar 2024",
        "Jun_2024": "Jun 2024",
        "Growth_2022_2024": "Growth %"
    }).sort_values("Growth %", ascending=False).reset_index(drop=True)
    display.index = display.index + 1
    st.dataframe(display.style.background_gradient(subset=["Growth %"], cmap="Greens"), use_container_width=True)
    st.download_button("⬇️ Download Maharashtra Data", df.to_csv(index=False), "maharashtra_districts.csv", "text/csv")

st.markdown("---")
st.markdown("<div class='gov-footer'>🏦 PMJDY Dashboard · District data: Rajya Sabha Questions 2022–2024 · Ministry of Finance, GoI</div>", unsafe_allow_html=True)
