import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import warnings
warnings.filterwarnings('ignore')

# ── Page Config ──
st.set_page_config(
    page_title="Jan Dhan Financial Inclusion Analysis",
    page_icon="🏦",
    layout="wide"
)

# ── Load Data from SQLite ──
@st.cache_data
def load_data():
    engine = create_engine('sqlite:///jandhan_analysis.db')
    df = pd.read_sql("""
        SELECT p.district, p.state, p.area_type,
               p.total_accounts_lakh, p.zero_balance_pct,
               p.avg_balance_inr, i.mgnrega_coverage_pct,
               i.banking_outlets_per_1000, i.bc_agents_per_1000,
               i.mobile_banking_pct
        FROM pmjdy_accounts p
        JOIN infrastructure i ON p.district_id = i.district_id
    """, engine)

    # ML Clustering
    features = df[[
        'zero_balance_pct', 'avg_balance_inr',
        'banking_outlets_per_1000', 'mgnrega_coverage_pct',
        'mobile_banking_pct'
    ]]
    scaler = StandardScaler()
    scaled = scaler.fit_transform(features)
    km = KMeans(n_clusters=3, random_state=42, n_init=10)
    df['cluster'] = km.fit_predict(scaled)
    cluster_means = df.groupby('cluster')['zero_balance_pct'].mean()
    sorted_clusters = cluster_means.sort_values()
    label_map = {
        sorted_clusters.index[0]: 'On Track',
        sorted_clusters.index[1]: 'Medium Priority',
        sorted_clusters.index[2]: 'High Priority'
    }
    df['intervention_tier'] = df['cluster'].map(label_map)
    return df

df = load_data()

# ── Colors ──
colors = {'Urban': '#1F4E79', 'Semi-Urban': '#2E86AB', 'Rural': '#E84855'}
tier_colors = {
    'High Priority': '#E84855',
    'Medium Priority': '#F4A261',
    'On Track': '#2A9D8F'
}

# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
st.markdown("""
    <h1 style='color:#1F4E79; margin-bottom:0'>
        🏦 Why Are Jan Dhan Accounts Lying Empty?
    </h1>
    <p style='color:#555; font-size:18px; margin-top:4px'>
        District-Level Financial Inclusion Analysis — India
    </p>
    <hr style='border:1px solid #1F4E79'>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# TOP KPI METRICS
# ─────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)

rural_zero = df[df['area_type']=='Rural']['zero_balance_pct'].mean()
urban_zero = df[df['area_type']=='Urban']['zero_balance_pct'].mean()
corr = df['mgnrega_coverage_pct'].corr(df['avg_balance_inr'])
gap = df[df['area_type']=='Urban']['banking_outlets_per_1000'].mean() / \
      df[df['area_type']=='Rural']['banking_outlets_per_1000'].mean()
high_priority = len(df[df['intervention_tier']=='High Priority'])

col1.metric("Rural Zero-Balance Rate", f"{rural_zero:.1f}%",
            f"{rural_zero/urban_zero:.1f}x higher than urban")
col2.metric("MGNREGA-Balance Correlation", f"{corr:.3f}",
            "Strong cash dependency")
col3.metric("Urban vs Rural Outlet Gap", f"{gap:.1f}x",
            "Urban has more banking access")
col4.metric("High Priority Districts", f"{high_priority}",
            "Need immediate intervention")

st.markdown("<br>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# SIDEBAR FILTERS
# ─────────────────────────────────────────────
st.sidebar.markdown("## 🔍 Filter Data")
selected_states = st.sidebar.multiselect(
    "Select States",
    options=sorted(df['state'].unique()),
    default=sorted(df['state'].unique())
)
selected_area = st.sidebar.multiselect(
    "Select Area Type",
    options=['Urban', 'Semi-Urban', 'Rural'],
    default=['Urban', 'Semi-Urban', 'Rural']
)
selected_tier = st.sidebar.multiselect(
    "Select Intervention Tier",
    options=['High Priority', 'Medium Priority', 'On Track'],
    default=['High Priority', 'Medium Priority', 'On Track']
)

filtered_df = df[
    (df['state'].isin(selected_states)) &
    (df['area_type'].isin(selected_area)) &
    (df['intervention_tier'].isin(selected_tier))
]

st.sidebar.markdown("---")
st.sidebar.markdown(f"**Showing {len(filtered_df)} of {len(df)} districts**")

# ─────────────────────────────────────────────
# ROW 1: CHARTS
# ─────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.markdown("#### Zero-Balance Rate by Area Type")
    fig, ax = plt.subplots(figsize=(6, 4))
    area_zero = filtered_df.groupby('area_type')['zero_balance_pct'].mean()
    bar_colors = [colors.get(a, '#888') for a in area_zero.index]
    bars = ax.bar(area_zero.index, area_zero.values,
                  color=bar_colors, width=0.5, edgecolor='white')
    for bar, val in zip(bars, area_zero.values):
        ax.text(bar.get_x() + bar.get_width()/2,
                bar.get_height() + 1, f'{val:.1f}%',
                ha='center', fontweight='bold')
    ax.set_ylabel('Avg Zero-Balance (%)')
    ax.set_ylim(0, 80)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.set_facecolor('#F8F9FA')
    fig.patch.set_facecolor('white')
    st.pyplot(fig)
    plt.close()

with col2:
    st.markdown("#### MGNREGA Coverage vs Avg Account Balance")
    fig, ax = plt.subplots(figsize=(6, 4))
    for area, grp in filtered_df.groupby('area_type'):
        ax.scatter(grp['mgnrega_coverage_pct'], grp['avg_balance_inr'],
                   color=colors.get(area, '#888'), label=area,
                   s=80, alpha=0.85, edgecolors='white')
    if len(filtered_df) > 1:
        z = np.polyfit(filtered_df['mgnrega_coverage_pct'],
                       filtered_df['avg_balance_inr'], 1)
        p = np.poly1d(z)
        x_line = np.linspace(filtered_df['mgnrega_coverage_pct'].min(),
                             filtered_df['mgnrega_coverage_pct'].max(), 100)
        ax.plot(x_line, p(x_line), 'gray', linestyle='--',
                linewidth=1.5, alpha=0.7)
    corr_filtered = filtered_df['mgnrega_coverage_pct'].corr(
        filtered_df['avg_balance_inr'])
    ax.set_title(f'r = {corr_filtered:.2f}', fontsize=10, color='gray')
    ax.set_xlabel('MGNREGA Coverage (%)')
    ax.set_ylabel('Avg Balance (INR)')
    ax.legend(title='Area Type')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.set_facecolor('#F8F9FA')
    fig.patch.set_facecolor('white')
    st.pyplot(fig)
    plt.close()

# ─────────────────────────────────────────────
# ROW 2: STATE + TIER
# ─────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.markdown("#### State-wise Zero-Balance Rate")
    fig, ax = plt.subplots(figsize=(6, 5))
    state_zero = filtered_df.groupby('state')['zero_balance_pct'] \
                            .mean().sort_values()
    bar_clrs = ['#E84855' if v > 40 else '#F4A261' if v > 25
                else '#2A9D8F' for v in state_zero.values]
    bars = ax.barh(state_zero.index, state_zero.values,
                   color=bar_clrs, edgecolor='white')
    ax.axvline(x=40, color='#E84855', linestyle='--',
               linewidth=1.2, alpha=0.6, label='40% threshold')
    for bar, val in zip(bars, state_zero.values):
        ax.text(val + 0.5, bar.get_y() + bar.get_height()/2,
                f'{val:.1f}%', va='center', fontsize=9)
    ax.legend()
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.set_facecolor('#F8F9FA')
    fig.patch.set_facecolor('white')
    st.pyplot(fig)
    plt.close()

with col2:
    st.markdown("#### ML District Segmentation — Intervention Tiers")
    fig, ax = plt.subplots(figsize=(6, 5))
    tier_counts = filtered_df['intervention_tier'].value_counts()
    wedge_colors = [tier_colors.get(t, '#888') for t in tier_counts.index]
    wedges, texts, autotexts = ax.pie(
        tier_counts.values,
        labels=tier_counts.index,
        colors=wedge_colors,
        autopct='%1.0f%%',
        startangle=90,
        pctdistance=0.75,
        wedgeprops={'edgecolor': 'white', 'linewidth': 2}
    )
    for text in texts:
        text.set_fontweight('bold')
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')
    fig.patch.set_facecolor('white')
    st.pyplot(fig)
    plt.close()

# ─────────────────────────────────────────────
# DISTRICT DATA TABLE
# ─────────────────────────────────────────────
st.markdown("---")
st.markdown("#### 📋 District-Level Data")

display_df = filtered_df[[
    'district', 'state', 'area_type',
    'zero_balance_pct', 'avg_balance_inr',
    'banking_outlets_per_1000', 'mgnrega_coverage_pct',
    'intervention_tier'
]].rename(columns={
    'district': 'District',
    'state': 'State',
    'area_type': 'Area',
    'zero_balance_pct': 'Zero Balance %',
    'avg_balance_inr': 'Avg Balance (INR)',
    'banking_outlets_per_1000': 'Outlets/1000',
    'mgnrega_coverage_pct': 'MGNREGA %',
    'intervention_tier': 'Tier'
}).sort_values('Zero Balance %', ascending=False)

st.dataframe(
    display_df.style.background_gradient(
        subset=['Zero Balance %'], cmap='RdYlGn_r'
    ),
    use_container_width=True
)

# ─────────────────────────────────────────────
# POLICY BRIEF
# ─────────────────────────────────────────────
st.markdown("---")
st.markdown("#### 📄 Policy Recommendations")

col1, col2, col3 = st.columns(3)

with col1:
    st.error("""
    **Finding 1 — Activation Gap**

    Rural districts show **2.3x higher** zero-balance
    rates than urban. India is succeeding at opening
    accounts but failing at activation.

    **Recommendation:** Shift targets from accounts
    opened to accounts actively transacting.
    Incentivize Business Correspondents per active
    account, not per account opened.
    """)

with col2:
    st.warning("""
    **Finding 2 — Cash Dependency**

    Correlation of **-0.964** between MGNREGA
    coverage and average balance. Wages arrive
    and are immediately withdrawn.

    **Recommendation:** Mandate DBT payment
    cycles keeping minimum balance in-account
    for 7 days. Pair with financial literacy
    camps at MGNREGA worksites.
    """)

with col3:
    st.success("""
    **Finding 3 — Infrastructure Gap**

    Urban areas have **5.1x more** banking
    outlets per capita than rural districts.

    **Recommendation:** Use this district
    segmentation model to prioritize BC
    network expansion in High Priority
    districts first.
    """)

st.markdown("---")
st.markdown(
    "<p style='color:gray; font-size:12px'>Data modelled on PMJDY public "
    "statistics (pmjdy.gov.in, data.gov.in) | "
    "Analysis by Tejaswini Shidheshwar Mathpati</p>",
    unsafe_allow_html=True
)