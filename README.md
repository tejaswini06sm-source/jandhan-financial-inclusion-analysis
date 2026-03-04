# 📊 Financial Inclusion Analysis Dashboard — India

An interactive data dashboard analyzing Pradhan Mantri Jan Dhan Yojana (PMJDY) 
financial inclusion performance across India using real government data.

🔗 **Live App:** https://tejaswini06sm-source-jandhan-financial-inclusion-ana-app-jhedko.streamlit.app

---

## 📌 About the Project

This project investigates why millions of Jan Dhan accounts remain zero-balance 
despite India's massive financial inclusion push. Using district-level data from 
Rajya Sabha parliamentary questions and Ministry of Finance reports, the dashboard 
surfaces patterns, gaps, and policy insights.

---

## 🔍 Key Findings

- Rural districts carry **2.3x higher zero-balance rates** than urban areas
- **−0.964 correlation** between MGNREGA coverage and average balance — indicating 
  deep cash dependency even where banking exists
- **5.1x gap** in banking infrastructure between urban and rural districts
- K-Means clustering segments states into High Performer / Developing / Needs Attention

---

## 📁 Dashboard Pages

1. 🏠 Home — National snapshot and key findings
2. 🗺️ National View — All states ranked by performance
3. 📍 State Analysis — Deep dive by state
4. 🏘️ District View — Bihar, Karnataka, Maharashtra districts
5. 👥 Gender Analysis — Male vs female account penetration
6. 💰 Balance Analysis — Distribution of account balances
7. 🤖 ML Insights — Clustering and anomaly detection
8. 📋 Policy Brief — Evidence-based recommendations for GoI

---

## 🛠️ Tech Stack

- **Python** — Pandas, NumPy, Scikit-learn
- **Visualization** — Plotly, Matplotlib, Seaborn
- **App** — Streamlit (deployed on Streamlit Cloud)
- **Data** — data.gov.in, Ministry of Finance, Rajya Sabha Q&A

---

## 📂 Project Structure
```
├── app.py                  # Main entry point
├── pages/                  # 8 dashboard pages
├── data/                   # Government CSV datasets
├── utils/                  # Data loader & ML models
└── assets/style.css        # Custom styling
```

---

## 🚀 Run Locally
```bash
git clone https://github.com/tejaswini06sm-source/jandhan-financial-inclusion-analysis
cd jandhan-financial-inclusion-analysis
pip install -r requirements.txt
streamlit run app.py
```

---

*Data Source: Ministry of Finance, GoI · Rajya Sabha Unstarred Questions 2022–2024*
