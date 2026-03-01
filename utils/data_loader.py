import pandas as pd
import numpy as np
import os

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")

STATE_POPULATION = {
    "Andaman and Nicobar Islands": 450000,
    "Andhra Pradesh": 54000000,
    "Arunachal Pradesh": 1700000,
    "Assam": 36000000,
    "Bihar": 130000000,
    "Chandigarh": 1200000,
    "Chhattisgarh": 32000000,
    "Dadra and Nagar Haveli and Daman and Diu": 700000,
    "Delhi": 32000000,
    "Goa": 1600000,
    "Gujarat": 72000000,
    "Haryana": 31000000,
    "Himachal Pradesh": 7500000,
    "Jammu and Kashmir": 14000000,
    "Jharkhand": 40000000,
    "Karnataka": 70000000,
    "Kerala": 36000000,
    "Ladakh": 300000,
    "Lakshadweep": 75000,
    "Madhya Pradesh": 90000000,
    "Maharashtra": 130000000,
    "Manipur": 3200000,
    "Meghalaya": 3800000,
    "Mizoram": 1300000,
    "Nagaland": 2200000,
    "Odisha": 47000000,
    "Puducherry": 1700000,
    "Punjab": 31000000,
    "Rajasthan": 82000000,
    "Sikkim": 700000,
    "Tamil Nadu": 80000000,
    "Telangana": 40000000,
    "Tripura": 4200000,
    "Uttar Pradesh": 240000000,
    "Uttarakhand": 11000000,
    "West Bengal": 100000000,
}

REGION_MAP = {
    "Andaman and Nicobar Islands": "Union Territory",
    "Andhra Pradesh": "South",
    "Arunachal Pradesh": "Northeast",
    "Assam": "Northeast",
    "Bihar": "East",
    "Chandigarh": "Union Territory",
    "Chhattisgarh": "Central",
    "Dadra and Nagar Haveli and Daman and Diu": "Union Territory",
    "Delhi": "Union Territory",
    "Goa": "West",
    "Gujarat": "West",
    "Haryana": "North",
    "Himachal Pradesh": "North",
    "Jammu and Kashmir": "North",
    "Jharkhand": "East",
    "Karnataka": "South",
    "Kerala": "South",
    "Ladakh": "Union Territory",
    "Lakshadweep": "Union Territory",
    "Madhya Pradesh": "Central",
    "Maharashtra": "West",
    "Manipur": "Northeast",
    "Meghalaya": "Northeast",
    "Mizoram": "Northeast",
    "Nagaland": "Northeast",
    "Odisha": "East",
    "Puducherry": "Union Territory",
    "Punjab": "North",
    "Rajasthan": "North",
    "Sikkim": "Northeast",
    "Tamil Nadu": "South",
    "Telangana": "South",
    "Tripura": "Northeast",
    "Uttar Pradesh": "North",
    "Uttarakhand": "North",
    "West Bengal": "East",
}


def _drop_serial_cols(df):
    for col in ["S.No", "S. No.", "Sl. No.", "Sl. No", "S.No.", "S.No"]:
        if col in df.columns:
            df = df.drop(columns=[col])
    return df


def load_state_data():
    df = pd.read_csv(os.path.join(DATA_DIR, "state_data.csv"), encoding="utf-8-sig")
    df.columns = df.columns.str.strip()
    df = _drop_serial_cols(df)
    # Handle both cleaned and original column names
    col_map = {}
    for c in df.columns:
        cs = c.strip()
        if "state" in cs.lower() or "ut" in cs.lower():
            col_map[c] = "State"
        elif "account" in cs.lower() and "number" in cs.lower():
            col_map[c] = "Accounts"
        elif "deposit" in cs.lower():
            col_map[c] = "Deposit_Crore"
        elif cs == "Accounts":
            col_map[c] = "Accounts"
        elif cs == "Deposit_Crore":
            col_map[c] = "Deposit_Crore"
    df = df.rename(columns=col_map)
    # Make sure we have the right columns
    if "State" not in df.columns:
        df.columns = ["State", "Accounts", "Deposit_Crore"]
    df = df[~df["State"].astype(str).str.lower().str.contains("total", na=False)].reset_index(drop=True)
    df["State"] = df["State"].astype(str).str.strip()
    df["Accounts"] = pd.to_numeric(df["Accounts"], errors="coerce")
    df["Deposit_Crore"] = pd.to_numeric(df["Deposit_Crore"], errors="coerce")
    df = df.dropna(subset=["Accounts", "Deposit_Crore"]).reset_index(drop=True)
    df["Population"] = df["State"].map(STATE_POPULATION).fillna(5000000)
    df["Region"] = df["State"].map(REGION_MAP).fillna("Other")
    df["Accounts_Per_1000"] = (df["Accounts"] / df["Population"] * 1000).round(1)
    df["Avg_Balance_INR"] = ((df["Deposit_Crore"] * 1e7) / df["Accounts"]).round(0)
    df["Accounts_Lakh"] = (df["Accounts"] / 1e5).round(2)
    df["Deposit_Rank"] = df["Deposit_Crore"].rank(ascending=False).astype(int)
    df["Accounts_Rank"] = df["Accounts"].rank(ascending=False).astype(int)
    df["Avg_Balance_Rank"] = df["Avg_Balance_INR"].rank(ascending=False).astype(int)
    df["Performance_Score"] = (
        (df["Accounts_Per_1000"] / df["Accounts_Per_1000"].max() * 50) +
        (df["Avg_Balance_INR"] / df["Avg_Balance_INR"].max() * 50)
    ).round(1)
    return df


def load_bihar_districts():
    df = pd.read_csv(os.path.join(DATA_DIR, "bihar_districts.csv"), encoding="utf-8-sig")
    df.columns = df.columns.str.strip()
    df = _drop_serial_cols(df)
    # Rename whatever columns exist to standard names
    col_map = {}
    for c in df.columns:
        cs = c.strip().lower()
        if "district" in cs:
            col_map[c] = "District"
        elif "account" in cs and "balance" not in cs:
            col_map[c] = "Accounts"
        elif "balance" in cs or "crore" in cs:
            col_map[c] = "Balance_Crore"
    df = df.rename(columns=col_map)
    if "District" not in df.columns:
        df.columns = ["District", "Accounts", "Balance_Crore"]
    df = df[~df["District"].astype(str).str.lower().str.contains("total|grand", na=False)].reset_index(drop=True)
    df["State"] = "Bihar"
    df["District"] = df["District"].astype(str).str.strip()
    df["Accounts"] = pd.to_numeric(df["Accounts"], errors="coerce")
    df["Balance_Crore"] = pd.to_numeric(df["Balance_Crore"], errors="coerce")
    df = df.dropna(subset=["Accounts", "Balance_Crore"]).reset_index(drop=True)
    df["Avg_Balance_INR"] = ((df["Balance_Crore"] * 1e7) / df["Accounts"]).round(0)
    df["Accounts_Lakh"] = (df["Accounts"] / 1e5).round(2)
    return df


def load_karnataka_districts():
    df = pd.read_csv(os.path.join(DATA_DIR, "karnataka_districts.csv"), encoding="utf-8-sig")
    df.columns = df.columns.str.strip()
    df = _drop_serial_cols(df)
    col_map = {}
    for c in df.columns:
        cs = c.strip().lower()
        if "district" in cs:
            col_map[c] = "District"
        elif "total" in cs and "account" in cs:
            col_map[c] = "Total_Accounts"
        elif "male" in cs and "female" not in cs:
            col_map[c] = "Male_Accounts"
        elif "female" in cs:
            col_map[c] = "Female_Accounts"
        elif "operative" in cs:
            col_map[c] = "Operative_Accounts"
    df = df.rename(columns=col_map)
    if "Total_Accounts" not in df.columns:
        cols = list(df.columns)
        # Assume order: District, Total, Male, Female, Operative
        mapping = ["District", "Total_Accounts", "Male_Accounts", "Female_Accounts", "Operative_Accounts"]
        df.columns = mapping[:len(cols)]
    df = df[~df["District"].astype(str).str.lower().str.contains("total", na=False)].reset_index(drop=True)
    df["State"] = "Karnataka"
    df["District"] = df["District"].astype(str).str.strip()
    for col in ["Total_Accounts", "Male_Accounts", "Female_Accounts", "Operative_Accounts"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    df["Inactive_Accounts"] = df["Total_Accounts"] - df["Operative_Accounts"]
    df["Inactive_Pct"] = ((df["Inactive_Accounts"] / df["Total_Accounts"]) * 100).round(1)
    df["Female_Pct"] = ((df["Female_Accounts"] / df["Total_Accounts"]) * 100).round(1)
    df["Male_Pct"] = ((df["Male_Accounts"] / df["Total_Accounts"]) * 100).round(1)
    df["Operative_Pct"] = ((df["Operative_Accounts"] / df["Total_Accounts"]) * 100).round(1)
    df["Accounts_Lakh"] = (df["Total_Accounts"] / 1e5).round(2)
    return df


def load_maharashtra_districts():
    df = pd.read_csv(os.path.join(DATA_DIR, "maharashtra_districts.csv"), encoding="utf-8-sig")
    df.columns = df.columns.str.strip()
    df = _drop_serial_cols(df)
    col_map = {}
    for c in df.columns:
        cs = c.strip().lower()
        if "district" in cs:
            col_map[c] = "District"
        elif "2022" in cs:
            col_map[c] = "Mar_2022"
        elif "2023" in cs:
            col_map[c] = "Mar_2023"
        elif "march 2024" in cs or "mar" in cs and "2024" in cs:
            col_map[c] = "Mar_2024"
        elif "june 2024" in cs or "jun" in cs:
            col_map[c] = "Jun_2024"
    df = df.rename(columns=col_map)
    # If still not renamed, use positional
    if "Mar_2022" not in df.columns:
        cols = list(df.columns)
        new_cols = ["District", "Mar_2022", "Mar_2023", "Mar_2024", "Jun_2024"]
        df.columns = new_cols[:len(cols)]
    df = df[~df["District"].astype(str).str.lower().str.contains("total", na=False)].reset_index(drop=True)
    df["State"] = "Maharashtra"
    df["District"] = df["District"].astype(str).str.strip()
    for col in ["Mar_2022", "Mar_2023", "Mar_2024", "Jun_2024"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    df["Growth_2022_2024"] = ((df["Mar_2024"] - df["Mar_2022"]) / df["Mar_2022"] * 100).round(1)
    df["Growth_2023_2024"] = ((df["Mar_2024"] - df["Mar_2023"]) / df["Mar_2023"] * 100).round(1)
    df["Accounts_Lakh_2024"] = (df["Mar_2024"] / 1e5).round(2)
    return df


def load_balance_distribution():
    df = pd.read_csv(os.path.join(DATA_DIR, "balance_distribution.csv"), encoding="utf-8-sig")
    df.columns = df.columns.str.strip()
    df = _drop_serial_cols(df)
    col_map = {}
    for c in df.columns:
        cs = c.strip().lower()
        if "particular" in cs or "slab" in cs or "category" in cs:
            col_map[c] = "Particulars"
        elif "crore" in cs or "amount" in cs or "rs" in cs:
            col_map[c] = "Amount_Crore"
    df = df.rename(columns=col_map)
    if "Amount_Crore" not in df.columns:
        df.columns = ["Particulars", "Amount_Crore"]
    df["Amount_Crore"] = pd.to_numeric(df["Amount_Crore"], errors="coerce")
    df = df.dropna(subset=["Amount_Crore"]).reset_index(drop=True)
    df["Pct"] = (df["Amount_Crore"] / df["Amount_Crore"].sum() * 100).round(1)
    return df


def load_all_districts():
    bihar = load_bihar_districts()[["District", "State", "Accounts", "Avg_Balance_INR", "Accounts_Lakh"]]
    karnataka = load_karnataka_districts()[["District", "State", "Total_Accounts", "Operative_Pct", "Female_Pct", "Accounts_Lakh"]].rename(columns={"Total_Accounts": "Accounts"})
    maha = load_maharashtra_districts()[["District", "State", "Mar_2024", "Growth_2022_2024", "Accounts_Lakh_2024"]].rename(columns={"Mar_2024": "Accounts", "Accounts_Lakh_2024": "Accounts_Lakh"})
    return bihar, karnataka, maha
