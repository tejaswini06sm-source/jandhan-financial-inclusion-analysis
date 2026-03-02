import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys, os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.data_loader import load_bihar_districts, load_karnataka_districts, load_maharashtra_districts
from utils.ml_models import detect_anomalies

st.set_page_config(page_title="District Explorer — PMJDY", page_icon="🏘️", layout="wide")

with open(os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "style.css"), encoding="utf-8") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

@st.cache_data
def get_data():
    return load_bihar_districts(), load_karnataka_districts(), load_maharashtra_districts()

bihar, karnataka, maharashtra = get_data()

with st.sidebar:
    st.page_link("app.py", label="🏠 Back to Home")
    st.markdown("---")
    st.markdown("## 🏘️ District Explorer")
    st.markdown("---")
    st.markdown("---")
    selected_state = st.radio("📍 Select State", ["Bihar", "Karnataka", "Maharashtra"])
    st.markdown("---")
    st.markdown("### 🔽 Filters")
    district_search = st.text_input("🔍 Search District", placeholder="Type district name...")
    top_n = st.slider("Show Top N districts in charts", min_value=5, max_value=38, value=10, step=5)
    sort_direction = st.radio("Sort order", ["Descending", "Ascending"], horizontal=True)
    st.markdown("---")
    st.markdown("<div class='info-box'><small>District data: Bihar (38), Karnataka (30), Maharashtra (36)</small></div>", unsafe_allow_html=True)

st.markdown("""
<div class='gov-header'>
    <h1 style='margin:0; font-size:24px;'>🏘️ District Explorer</h1>
    <p style='margin:5px 0 0 0; opacity:0.9;'>Search, compare and analyse districts — Bihar · Karnataka · Maharashtra</p>
</div>
""", unsafe_allow_html=True)

asc = (sort_direction == "Ascending")

if selected_state == "Bihar":
    df = bihar.copy()
    df = detect_anomalies(df, "Accounts", "Balance_Crore")
    if district_search:
        df = df[df["District"].str.contains(district_search, case=False, na=False)]

    st.markdown("### 📍 Bihar — District Analysis")
    st.markdown("<div class='info-box'>Data: Rajya Sabha Unstarred Question No. 246, 2022.</div>", unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Districts Shown", len(df))
    col2.metric("Total Accounts", f"{df['Accounts'].sum()/1e5:.0f} Lakh")
    col3.metric("Total Balance", f"₹{df['Balance_Crore'].sum():.0f} Cr")
    col4.metric("Avg Balance/Account", f"₹{df['Avg_Balance_INR'].mean():.0f}")

    # Sort metric selector
    sort_metric = st.radio("Sort districts by:", ["Accounts", "Avg_Balance_INR", "Balance_Crore"], horizontal=True,
                            format_func=lambda x: {"Accounts": "Total Accounts", "Avg_Balance_INR": "Avg Balance", "Balance_Crore": "Total Balance"}[x])

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**Top {top_n} Districts by {sort_metric.replace('_',' ')}**")
        top_df = df.nlargest(top_n, sort_metric).sort_values(sort_metric, ascending=asc)
        fig = px.bar(top_df, x=sort_metric, y="District", orientation="h",
                     color="Avg_Balance_INR", color_continuous_scale="Blues",
                     labels={sort_metric: sort_metric.replace("_"," "), "Avg_Balance_INR": "Avg Balance (₹)"}, height=400)
        fig.update_layout(plot_bgcolor="#F8F9FA", paper_bgcolor="white")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("**Accounts vs Balance — Anomaly Scatter**")
        anomaly_filter = st.multiselect("Filter anomaly type:", df["Anomaly_Type"].unique().tolist(), default=df["Anomaly_Type"].unique().tolist())
        scatter_df = df[df["Anomaly_Type"].isin(anomaly_filter)]
        fig2 = px.scatter(scatter_df, x="Accounts", y="Avg_Balance_INR", hover_name="District",
                          size="Accounts", color="Anomaly_Type",
                          color_discrete_map={"Normal": "#2A9D8F", "Unusually High": "#E76F51", "Unusually Low": "#F4A261"},
                          labels={"Accounts": "Total Accounts", "Avg_Balance_INR": "Avg Balance (₹)"}, height=400)
        fig2.update_layout(plot_bgcolor="#F8F9FA", paper_bgcolor="white")
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("**📋 Full Bihar District Data**")
    bal_range = st.slider("Filter by Avg Balance (₹):", int(df["Avg_Balance_INR"].min()), int(df["Avg_Balance_INR"].max()),
                           (int(df["Avg_Balance_INR"].min()), int(df["Avg_Balance_INR"].max())))
    display = df[df["Avg_Balance_INR"].between(bal_range[0], bal_range[1])][
        ["District", "Accounts", "Accounts_Lakh", "Balance_Crore", "Avg_Balance_INR", "Anomaly_Type"]
    ].rename(columns={"Accounts_Lakh": "Accounts (Lakh)", "Balance_Crore": "Balance (Cr)", "Avg_Balance_INR": "Avg Balance (₹)", "Anomaly_Type": "Pattern"}
    ).sort_values("Avg Balance (₹)", ascending=asc).reset_index(drop=True)
    display.index = display.index + 1
    st.dataframe(display.style.background_gradient(subset=["Avg Balance (₹)"], cmap="Greens"), use_container_width=True)
    st.download_button("⬇️ Download Bihar Data", df.to_csv(index=False), "bihar_districts.csv", "text/csv")

elif selected_state == "Karnataka":
    df = karnataka.copy()
    df = detect_anomalies(df, "Total_Accounts")
    if district_search:
        df = df[df["District"].str.contains(district_search, case=False, na=False)]

    st.markdown("### 📍 Karnataka — District Analysis")
    st.markdown("<div class='info-box'>Data: Rajya Sabha Unstarred Question No. 2313, 2023.</div>", unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Districts Shown", len(df))
    col2.metric("Total Accounts", f"{df['Total_Accounts'].sum()/1e5:.0f} Lakh")
    col3.metric("Avg Operative %", f"{df['Operative_Pct'].mean():.1f}%")
    col4.metric("Avg Female %", f"{df['Female_Pct'].mean():.1f}%")

    # Operative % filter
    op_range = st.slider("Filter by Operative % range:", 0, 100, (0, 100))
    df_filtered = df[df["Operative_Pct"].between(op_range[0], op_range[1])]

    sort_metric_k = st.radio("Sort districts by:", ["Total_Accounts", "Operative_Pct", "Female_Pct", "Inactive_Pct"], horizontal=True,
                              format_func=lambda x: {"Total_Accounts": "Total Accounts", "Operative_Pct": "Operative %", "Female_Pct": "Female %", "Inactive_Pct": "Inactive %"}[x])

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**Operative vs Inactive — Top {top_n} Districts**")
        df_sorted = df_filtered.sort_values("Operative_Pct", ascending=asc).tail(top_n)
        fig = go.Figure()
        fig.add_trace(go.Bar(name="Operative", y=df_sorted["District"], x=df_sorted["Operative_Accounts"], orientation="h", marker_color="#2A9D8F"))
        fig.add_trace(go.Bar(name="Inactive", y=df_sorted["District"], x=df_sorted["Inactive_Accounts"], orientation="h", marker_color="#E76F51"))
        fig.update_layout(barmode="stack", height=500, plot_bgcolor="#F8F9FA", paper_bgcolor="white", xaxis_title="Number of Accounts")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("**Female Account Share by District**")
        fig2 = px.bar(df_filtered.sort_values("Female_Pct", ascending=asc),
                      x="Female_Pct", y="District", orientation="h",
                      color="Female_Pct", color_continuous_scale="RdYlGn", range_color=[40, 60],
                      labels={"Female_Pct": "Female Accounts (%)", "District": ""}, height=500)
        fig2.add_vline(x=50, line_dash="dash", line_color="#1F4E79", annotation_text="50% parity")
        fig2.update_layout(plot_bgcolor="#F8F9FA", paper_bgcolor="white")
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("**📋 Full Karnataka District Data**")
    display = df_filtered[["District", "Total_Accounts", "Male_Accounts", "Female_Accounts",
                            "Operative_Accounts", "Female_Pct", "Operative_Pct", "Inactive_Pct"]].rename(columns={
        "Total_Accounts": "Total", "Male_Accounts": "Male", "Female_Accounts": "Female",
        "Operative_Accounts": "Operative", "Female_Pct": "Female %", "Operative_Pct": "Operative %", "Inactive_Pct": "Inactive %"
    }).sort_values(sort_metric_k.replace("_Pct", " %").replace("_Accounts", "").replace("Total_Accounts","Total"), ascending=asc).reset_index(drop=True)
    display.index = display.index + 1
    st.dataframe(display.style.background_gradient(subset=["Operative %"], cmap="Greens"), use_container_width=True)
    st.download_button("⬇️ Download Karnataka Data", df.to_csv(index=False), "karnataka_districts.csv", "text/csv")

elif selected_state == "Maharashtra":
    df = maharashtra.copy()
    if district_search:
        df = df[df["District"].str.contains(district_search, case=False, na=False)]

    st.markdown("### 📍 Maharashtra — 4-Year Trend (2022–2024)")
    st.markdown("<div class='info-box'>Data: Rajya Sabha Unstarred Question No. 886, 2024. 4-point time series: Mar 2022, Mar 2023, Mar 2024, Jun 2024.</div>", unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Districts Shown", len(df))
    col2.metric("Accounts (Jun 2024)", f"{df['Jun_2024'].sum()/1e5:.0f} Lakh")
    col3.metric("Avg 2yr Growth", f"{df['Growth_2022_2024'].mean():.1f}%")
    col4.metric("Fastest Growing", df.loc[df["Growth_2022_2024"].idxmax(), "District"])

    # Growth range filter
    g_min = float(df["Growth_2022_2024"].min())
    g_max = float(df["Growth_2022_2024"].max())
    growth_range = st.slider("Filter by Growth % (2022→2024):", round(g_min), round(g_max), (round(g_min), round(g_max)))
    df_filtered = df[df["Growth_2022_2024"].between(growth_range[0], growth_range[1])]

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**Top {top_n} Districts by Growth %**")
        top_df = df_filtered.nlargest(top_n, "Growth_2022_2024").sort_values("Growth_2022_2024", ascending=asc)
        fig = px.bar(top_df, x="Growth_2022_2024", y="District", orientation="h",
                     color="Growth_2022_2024", color_continuous_scale="RdYlGn",
                     labels={"Growth_2022_2024": "Growth % (2022→2024)", "District": ""}, height=500)
        fig.update_layout(plot_bgcolor="#F8F9FA", paper_bgcolor="white")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("**Select District — 4-Year Trend**")
        district_options = sorted(df["District"].tolist())
        selected_district = st.selectbox("Choose District", district_options)
        row = df[df["District"] == selected_district].iloc[0]
        trend_data = pd.DataFrame({
            "Period": ["Mar 2022", "Mar 2023", "Mar 2024", "Jun 2024"],
            "Accounts": [row["Mar_2022"], row["Mar_2023"], row["Mar_2024"], row["Jun_2024"]]
        }).dropna()
        fig2 = px.line(trend_data, x="Period", y="Accounts", markers=True,
                       title=f"{selected_district} — Account Growth Trend",
                       labels={"Accounts": "PMJDY Accounts", "Period": ""}, height=350)
        fig2.update_traces(line_color="#1F4E79", marker_size=10)
        fig2.update_layout(plot_bgcolor="#F8F9FA", paper_bgcolor="white")
        st.plotly_chart(fig2, use_container_width=True)
        if pd.notna(row["Growth_2022_2024"]):
            st.metric("2-Year Growth", f"{row['Growth_2022_2024']:.1f}%", f"vs state avg {df['Growth_2022_2024'].mean():.1f}%")

    # Multi-district comparison
    st.markdown("---")
    st.markdown("**📊 Compare Multiple Districts**")
    compare_districts = st.multiselect("Select districts to compare:", sorted(df["District"].tolist()), default=sorted(df["District"].tolist())[:5])
    if compare_districts:
        comp_df = df[df["District"].isin(compare_districts)].melt(
            id_vars="District", value_vars=["Mar_2022", "Mar_2023", "Mar_2024", "Jun_2024"],
            var_name="Period", value_name="Accounts"
        ).dropna()
        comp_df["Period"] = comp_df["Period"].map({"Mar_2022": "Mar 2022", "Mar_2023": "Mar 2023", "Mar_2024": "Mar 2024", "Jun_2024": "Jun 2024"})
        fig3 = px.line(comp_df, x="Period", y="Accounts", color="District", markers=True, height=400)
        fig3.update_layout(plot_bgcolor="#F8F9FA", paper_bgcolor="white")
        st.plotly_chart(fig3, use_container_width=True)

    st.markdown("**📋 Full Maharashtra District Data**")
    display = df_filtered[["District", "Mar_2022", "Mar_2023", "Mar_2024", "Jun_2024", "Growth_2022_2024"]].rename(columns={
        "Mar_2022": "Mar 2022", "Mar_2023": "Mar 2023", "Mar_2024": "Mar 2024", "Jun_2024": "Jun 2024", "Growth_2022_2024": "Growth %"
    }).sort_values("Growth %", ascending=asc).reset_index(drop=True)
    display.index = display.index + 1
    st.dataframe(display.style.background_gradient(subset=["Growth %"], cmap="Greens"), use_container_width=True)
    st.download_button("⬇️ Download Maharashtra Data", df.to_csv(index=False), "maharashtra_districts.csv", "text/csv")

st.markdown("---")
st.markdown("<div class='gov-footer'>🏦 PMJDY Dashboard · District data: Rajya Sabha Questions 2022–2024 · Ministry of Finance, GoI</div>", unsafe_allow_html=True)