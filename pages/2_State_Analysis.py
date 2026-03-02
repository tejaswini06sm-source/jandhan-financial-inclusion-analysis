import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys, os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.data_loader import load_state_data

st.set_page_config(page_title="State Analysis — PMJDY", page_icon="📊", layout="wide")

with open(os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "style.css"), encoding="utf-8") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

@st.cache_data
def get_data():
    return load_state_data()

df = get_data()

with st.sidebar:
    st.markdown("## 📊 State Analysis")
    st.markdown("---")
    st.markdown("---")
    st.markdown("### 🔽 Filters")
    state_search = st.text_input("🔍 Search State", placeholder="Type to filter...")
    filtered_states = sorted([s for s in df["State"].tolist() if state_search.lower() in s.lower()]) if state_search else sorted(df["State"].tolist())
    selected_state = st.selectbox("📍 Select Primary State", filtered_states)
    st.markdown("---")
    compare_mode = st.checkbox("⚖️ Compare with another state", value=False)
    if compare_mode:
        compare_state = st.selectbox("Compare with", [s for s in sorted(df["State"].tolist()) if s != selected_state])
    st.markdown("---")
    st.markdown("**Chart Options**")
    chart_sort = st.selectbox("National context — sort by",
        ["Avg_Balance_INR", "Accounts_Per_1000", "Accounts_Lakh", "Performance_Score"],
        format_func=lambda x: {"Avg_Balance_INR": "Avg Balance", "Accounts_Per_1000": "Coverage/1000",
                                "Accounts_Lakh": "Total Accounts", "Performance_Score": "Performance Score"}[x])
    highlight_color = st.color_picker("Highlight color", "#E74C3C")
    st.markdown("---")
    st.markdown("**Peer Comparison**")
    peer_metric = st.selectbox("Rank peers by", ["Performance_Score", "Avg_Balance_INR", "Accounts_Per_1000"],
        format_func=lambda x: {"Performance_Score": "Performance Score", "Avg_Balance_INR": "Avg Balance", "Accounts_Per_1000": "Coverage/1000"}[x])
    show_all_regions = st.checkbox("Show all regions as peers", value=False)

st.markdown("""
<div class='gov-header'>
    <h1 style='margin:0; font-size:24px;'>📊 State Deep Dive</h1>
    <p style='margin:5px 0 0 0; opacity:0.9;'>Detailed analysis for any state — accounts, deposits, rankings, and peer comparison</p>
</div>
""", unsafe_allow_html=True)

state_data = df[df["State"] == selected_state].iloc[0]

st.markdown(f"## 📋 {selected_state} — Scorecard")
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Total Accounts", f"{state_data['Accounts']/1e5:.1f} Lakh")
col2.metric("Total Deposits", f"₹{state_data['Deposit_Crore']:.0f} Cr")
col3.metric("Avg Balance", f"₹{state_data['Avg_Balance_INR']:.0f}")
col4.metric("Accounts/1000 pop", f"{state_data['Accounts_Per_1000']:.1f}")
col5.metric("Performance Score", f"{state_data['Performance_Score']:.1f}/100")

nat_avg_bal = df['Avg_Balance_INR'].mean()
nat_avg_cov = df['Accounts_Per_1000'].mean()
col1, col2, col3, col4 = st.columns(4)
col1.markdown(f"**National Rank (Accounts):** #{state_data['Accounts_Rank']} of 36")
col2.markdown(f"**National Rank (Avg Balance):** #{state_data['Avg_Balance_Rank']} of 36")
col3.metric("vs National Avg Balance", f"₹{state_data['Avg_Balance_INR'] - nat_avg_bal:+.0f}", f"Nat avg: ₹{nat_avg_bal:.0f}")
col4.metric("vs National Avg Coverage", f"{state_data['Accounts_Per_1000'] - nat_avg_cov:+.1f}/1000", f"Nat avg: {nat_avg_cov:.0f}")

st.markdown("<p class='source-tag'>Source: Ministry of Finance, Rajya Sabha Q239, 2024</p>", unsafe_allow_html=True)
st.markdown("---")

if compare_mode:
    compare_data = df[df["State"] == compare_state].iloc[0]
    st.markdown(f"### ⚖️ {selected_state} vs {compare_state}")
    metrics = ["Accounts", "Deposit_Crore", "Avg_Balance_INR", "Accounts_Per_1000", "Performance_Score"]
    labels = ["Total Accounts", "Deposits (Cr)", "Avg Balance (₹)", "Accounts/1000", "Performance Score"]
    vals1 = [state_data[m] for m in metrics]
    vals2 = [compare_data[m] for m in metrics]
    max_vals = [max(v1, v2) for v1, v2 in zip(vals1, vals2)]
    norm1 = [v/m*100 if m > 0 else 0 for v, m in zip(vals1, max_vals)]
    norm2 = [v/m*100 if m > 0 else 0 for v, m in zip(vals2, max_vals)]
    fig = go.Figure()
    fig.add_trace(go.Bar(name=selected_state, x=labels, y=norm1, marker_color=highlight_color,
                         text=[f"{v:,.0f}" for v in vals1], textposition="outside"))
    fig.add_trace(go.Bar(name=compare_state, x=labels, y=norm2, marker_color="#2E86AB",
                         text=[f"{v:,.0f}" for v in vals2], textposition="outside"))
    fig.update_layout(barmode="group", plot_bgcolor="#F8F9FA", paper_bgcolor="white", yaxis_title="Relative Score (%)", height=400)
    st.plotly_chart(fig, use_container_width=True)
    summary = [{"Metric": l, selected_state: f"{v1:,.0f}", compare_state: f"{v2:,.0f}", "Winner 🏆": selected_state if v1 > v2 else compare_state}
               for l, m, v1, v2 in zip(labels, metrics, vals1, vals2)]
    st.dataframe(pd.DataFrame(summary), hide_index=True, use_container_width=True)
    st.markdown("---")

st.markdown(f"### 📍 {selected_state} in National Context")
col1, col2 = st.columns(2)
label_map = {"Avg_Balance_INR": "Avg Balance (₹)", "Accounts_Per_1000": "Accounts per 1,000", "Accounts_Lakh": "Total Accounts (Lakh)", "Performance_Score": "Performance Score"}
with col1:
    fig_rank = px.bar(df.sort_values(chart_sort), x=chart_sort, y="State", orientation="h",
        color=df.sort_values(chart_sort)["State"].apply(lambda s: "Selected" if s == selected_state else "Others"),
        color_discrete_map={"Selected": highlight_color, "Others": "#AED6F1"}, height=650,
        labels={chart_sort: label_map[chart_sort], "State": ""})
    fig_rank.update_layout(showlegend=False, plot_bgcolor="#F8F9FA", paper_bgcolor="white")
    st.plotly_chart(fig_rank, use_container_width=True)

with col2:
    st.markdown(f"**{selected_state} — Performance Radar vs National Avg**")
    categories = ["Avg Balance", "Coverage/1000", "Total Accounts", "Deposits", "Perf Score"]
    def norm(val, col):
        mn, mx = df[col].min(), df[col].max()
        return (val - mn) / (mx - mn) * 100 if mx > mn else 50
    cols = ["Avg_Balance_INR", "Accounts_Per_1000", "Accounts_Lakh", "Deposit_Crore", "Performance_Score"]
    vals_sel = [norm(state_data[c], c) for c in cols]
    vals_nat = [norm(df[c].mean(), c) for c in cols]
    fig_radar = go.Figure()
    fig_radar.add_trace(go.Scatterpolar(r=vals_sel+[vals_sel[0]], theta=categories+[categories[0]], fill='toself', name=selected_state, line_color=highlight_color))
    fig_radar.add_trace(go.Scatterpolar(r=vals_nat+[vals_nat[0]], theta=categories+[categories[0]], fill='toself', name="National Avg", line_color="#2E86AB", opacity=0.5))
    fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), showlegend=True, paper_bgcolor="white", height=400)
    st.plotly_chart(fig_radar, use_container_width=True)

st.markdown("---")
region = state_data["Region"]
peers = df if show_all_regions else df[df["Region"] == region]
peer_title = "All States" if show_all_regions else f"{region} Region"
st.markdown(f"### 🤝 {selected_state} vs {peer_title} Peers — sorted by {label_map.get(peer_metric, peer_metric)}")

def highlight_selected(row):
    return ['background-color: #FFF3CD' if row['State'] == selected_state else '' for _ in row]

peer_display = peers[["State", "Accounts_Lakh", "Deposit_Crore", "Avg_Balance_INR", "Accounts_Per_1000", "Performance_Score"]].rename(columns={
    "Accounts_Lakh": "Accounts (Lakh)", "Deposit_Crore": "Deposits (Cr)", "Avg_Balance_INR": "Avg Balance (₹)",
    "Accounts_Per_1000": "Per 1000 Pop", "Performance_Score": "Score /100"
}).sort_values("Score /100", ascending=False).reset_index(drop=True)
peer_display.index = peer_display.index + 1
st.dataframe(peer_display.style.apply(highlight_selected, axis=1).background_gradient(subset=["Score /100"], cmap="Greens"), use_container_width=True)
st.markdown("<small>🟡 Yellow = selected state</small>", unsafe_allow_html=True)

st.markdown("---")
col1, col2 = st.columns(2)
with col1:
    st.download_button("⬇️ Download All State Data", df.to_csv(index=False), "pmjdy_all_states.csv", "text/csv")
with col2:
    st.download_button(f"⬇️ Download {selected_state} Data", df[df["State"]==selected_state].to_csv(index=False), f"pmjdy_{selected_state.lower().replace(' ','_')}.csv", "text/csv")

st.markdown("---")
st.markdown("<div class='gov-footer'>🏦 PMJDY Dashboard · Source: Ministry of Finance, GoI · Data: 2024</div>", unsafe_allow_html=True)