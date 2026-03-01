import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
import warnings
warnings.filterwarnings("ignore")


def cluster_states(df):
    """K-Means clustering of states into performance tiers"""
    features = df[["Accounts_Per_1000", "Avg_Balance_INR", "Performance_Score"]].dropna()
    scaler = StandardScaler()
    scaled = scaler.fit_transform(features)
    km = KMeans(n_clusters=3, random_state=42, n_init=10)
    clusters = km.fit_predict(scaled)
    temp = df.loc[features.index].copy()
    temp["Cluster"] = clusters
    means = temp.groupby("Cluster")["Performance_Score"].mean().sort_values()
    label_map = {
        means.index[0]: "Needs Attention",
        means.index[1]: "Developing",
        means.index[2]: "High Performer",
    }
    df = df.copy()
    df["Tier"] = df.index.map(lambda i: label_map.get(clusters[list(features.index).index(i)], "Unknown") if i in features.index else "Unknown")
    return df


def predict_underperformers(df):
    """Identify states underperforming vs their population potential"""
    df = df.copy()
    df["Expected_Accounts"] = df["Population"] * 0.45  # 45% coverage target
    df["Coverage_Pct"] = (df["Accounts"] / df["Population"] * 100).round(1)
    df["Gap_Lakh"] = ((df["Expected_Accounts"] - df["Accounts"]) / 1e5).round(1)
    df["Underperforming"] = df["Gap_Lakh"] > 0
    return df


def growth_predictor(df_maha):
    """Predict when Maharashtra districts will reach saturation (based on trend)"""
    results = []
    for _, row in df_maha.iterrows():
        district = row["District"]
        points = []
        for year, col in [(2022, "Mar_2022"), (2023, "Mar_2023"), (2024, "Mar_2024")]:
            if pd.notna(row[col]):
                points.append((year, row[col]))
        if len(points) >= 2:
            X = np.array([p[0] for p in points]).reshape(-1, 1)
            y = np.array([p[1] for p in points])
            model = LinearRegression().fit(X, y)
            annual_growth = model.coef_[0]
            current = row["Mar_2024"] if pd.notna(row["Mar_2024"]) else row["Jun_2024"]
            target = current * 1.2  # 20% more as target
            if annual_growth > 0:
                years_needed = (target - current) / annual_growth
                target_year = int(2024 + years_needed)
            else:
                target_year = None
            growth_pct = row.get("Growth_2022_2024", None)
            results.append({
                "District": district,
                "Current_Accounts": current,
                "Annual_Growth": round(annual_growth),
                "Target_Year": target_year,
                "Growth_Pct_2yr": growth_pct,
            })
    return pd.DataFrame(results)


def detect_anomalies(df, account_col="Accounts", balance_col=None):
    """Flag districts with unusual patterns using z-score"""
    df = df.copy()
    df["Z_Score"] = (df[account_col] - df[account_col].mean()) / df[account_col].std()
    df["Anomaly"] = df["Z_Score"].abs() > 2
    df["Anomaly_Type"] = df["Z_Score"].apply(
        lambda z: "Unusually High" if z > 2 else ("Unusually Low" if z < -2 else "Normal")
    )
    return df
