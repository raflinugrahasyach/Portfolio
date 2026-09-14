# 🚲 Capital Bikeshare Demand Intelligence: Interactive Streamlit Analytics Dashboard

## 📖 Overview & Urban Mobility Impact
Micro-mobility sharing systems serve as critical transit infrastructure in modern metropolitan areas, offering sustainable first- and last-mile connectivity and relieving pressure on municipal road networks. For bike-share fleet operators, the primary logistical hurdle is **dynamic fleet rebalancing**: ensuring docking stations in commercial employment centers do not run empty during morning inbound commutes while preventing residential origin docks from overflowing in the evening.

This project delivers an interactive **Streamlit Operational Analytics Dashboard** conducting deep explanatory data analysis (EDA) across multi-year hourly and daily rental transactions from the **Capital Bikeshare** network. The application translates raw mobility records into actionable fleet allocation strategies by analyzing temporal commuter behaviors, seasonal shifts, and microclimate environmental dependencies.

---

## 🛠️ Architecture & Technology Stack
- **Web Analytics Framework**: Streamlit (`app.py`).
- **Data Engineering & Analytics**: Python 3, Pandas, NumPy (`df_day_clean.csv`, `df_hour_clean.csv`).
- **Data Visualization Suite**: Matplotlib, Seaborn.
- **Runtime Environment**: Containerized Python runtime (`requirements.txt`, `runtime.txt`).

---

## 🔄 Methodology & Analytical Pipeline

```
Raw Rental Transaction Logs (df_day.csv & df_hour.csv)
                          │
                          ▼
        Automated Data Cleaning & Feature Derivation
        ├── Temporal Indexing & Working Day / Holiday Segmentation
        ├── Weather Categorization & Thermal Normalization
        └── User Decomposition: Registered Commuters vs. Casual Users
                          │
                          ▼
       Cleaned Analytical Data Layer (df_day_clean.csv, df_hour_clean.csv)
                          │
                          ▼
       Streamlit Interactive Analytics Engine (app.py)
        ├── Dynamic Date Range Sidebar Filtering
        ├── High-Level Operational KPI Cards
        ├── Diurnal Hourly Rush-Hour Decomposition
        └── Environmental & Meteorological Sensitivity Models
```

---

## 📊 Key Dashboard Features & Empirical Insights
- **Bimodal Commuter Surge (Weekday Dynamics)**: Hourly rental distributions display sharp, distinct bimodal peaks at **08:00 AM** and **05:00–06:00 PM** on business days, driven by registered subscribers commuting between residential hubs and downtown commercial offices.
- **Unimodal Weekend Leisure Curves**: On non-working days and weekends, demand transforms into a broad, unimodal curve peaking between **12:00 PM and 04:00 PM**, dominated by casual tourists and recreational riders.
- **Meteorological Sensitivity**:
  - Positive linear correlation with ambient temperature up to an optimal thermal comfort threshold (~25°C), beyond which extreme summer heat slightly dampens rides.
  - Severe adverse weather situations (heavy precipitation, thunderstorms, snow) cause immediate **>70% drops** in total daily fleet utilization.
- **Dynamic Interactive Exploration**: Users can filter temporal spans via the sidebar date widget, instantly recalculating total ridership, average daily fleet demand, and user segment ratios.

---

## 🚀 How to Run Locally

### 1. Install Required Packages
```bash
pip install streamlit pandas numpy matplotlib seaborn
```

### 2. Launch Streamlit Server
```bash
streamlit run app.py
```

### 3. Access Dashboard
The application will automatically launch your default web browser at `http://localhost:8501`. Use the left sidebar to calibrate dates and inspect real-time visualizations.

---

## 🖼️ Dashboard Interface & Mobility Metrics
![Project Preview](./preview.png)
