# 🌾 Regional Agricultural Commodity Yield & Harvest Seasonality: Tableau Analytical Dashboard

## 📖 Overview & Business Value
Agricultural commodity markets are susceptible to extreme supply shocks and price volatility caused by localized weather deviations, shifting crop acreage, and harvest timing mismatches. In regional agrarian economies, agricultural planning agencies and supply-chain distributors require continuous visibility into commodity harvest yields, district land-use efficiency, and cyclical production schedules to maintain food security reserves and stabilize market pricing.

This project delivers an interactive **Business Intelligence (BI) Analytics Dashboard** built in **Tableau Desktop**, backed by an automated Python data-cleaning and transformation pipeline (`data_cleaning.py`). The dashboard enables policymakers and agricultural logistics planners to evaluate multi-commodity harvest volumes, track yield per hectare, and detect seasonal supply anomalies across regional administrative districts.

---

## 🛠️ Architecture & Technology Stack
- **Business Intelligence & Visual Analytics**: Tableau Desktop / Tableau Public (`Dashboard_Hasil_Panen_Extract.twbx`, `produksi.twb`).
- **Data Engineering & ETL Pipeline**: Python 3, Pandas, OpenPyXL (`data_cleaning.py`).
- **Structured Data Layer**: Normalized agricultural registry (`Database_Panen_Clean.xlsx`).
- **Visual Design Paradigm**: Executive KPI summary cards, coordinated dual-axis trend lines, and interactive spatial district breakdowns.

---

## 🔄 Methodology & System Flow

```
Raw Agricultural Census Records
              │
              ▼
   Python ETL Pipeline (data_cleaning.py)
   ├── Null Imputation & Outlier Validation
   ├── Metric Standardization (Tons, Hectares, Quintals)
   └── Relational Data Structuring
              │
              ▼
   Cleaned Database Layer (Database_Panen_Clean.xlsx)
              │
              ▼
   Tableau Hyper / Packaged Extract (.twbx)
              │
              ▼
   Interactive Executive Dashboard
   ├── KPI Performance Metrics (Total Yield, Active Land Area)
   ├── Temporal Seasonality & Crop Harvest Trajectories
   └── Cross-Commodity Yield Efficiency Comparison
```

---

## 📊 Key Dashboard Features & Analytical Insights
- **Dynamic Multi-Parameter Slicers**: Interactive filtering across agricultural commodity categories (e.g., staple grains, horticulture, cash crops), administrative regencies, and seasonal calendar quarters.
- **Land Productivity Metrics (Yield/Hectare)**: Isolates districts experiencing declining crop yield efficiency despite steady harvested land area, providing early detection of soil degradation or localized pest outbreaks.
- **Harvest Seasonality Curves**: Multi-year overlay line charts tracking historical harvest peaks and post-harvest supply lulls, supporting proactive warehousing and cold-chain logistical reservations.

---

## 🚀 How to Open & Deploy

### Option 1: Tableau Desktop / Public Viewer
1. Install [Tableau Desktop](https://www.tableau.com/products/desktop) or [Tableau Public Viewer](https://public.tableau.com/).
2. Double-click to launch `Dashboard_Hasil_Panen_Extract.twbx` (contains embedded extracts).
3. Interact with the visual filters, date range parameters, and commodity selectors.

### Option 2: Run Python ETL Pipeline
```bash
pip install pandas openpyxl
python data_cleaning.py
```

---

## 🖼️ Executive Dashboard Preview
![Project Preview](./preview.png)
