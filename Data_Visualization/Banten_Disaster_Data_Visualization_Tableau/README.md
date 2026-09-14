# 🌊 Multi-Year Geospatial Natural Disaster Risk & Damage Analytics: Tableau BI System (Banten Province 2021–2023)

## 📖 Overview & Civic Impact
Banten Province, situated along the Sunda Strait tectonic boundary and western Java river basins, faces recurring natural hazards ranging from hydrometeorological crises (flash floods, tidal storm surges, river overflows) to geophysical disruptions (landslides and seismic tremors). Regional disaster management authorities (**BPBD**) and public works departments require quantitative visual systems to monitor multi-year disaster patterns, quantify infrastructural losses, and allocate emergency response budgets based on empirical risk profiles.

This project delivers a comprehensive **Tableau Business Intelligence (BI) Analytics System** synthesizing longitudinal disaster datasets across 2021–2023 for all eight administrative regencies and cities in Banten (**Lebak, Pandeglang, Serang, Tangerang, Cilegon, South Tangerang, etc.**). The system provides municipal leadership with interactive tools to assess geographic vulnerability, track residential structural damage, and prioritize disaster-resilient infrastructure investments.

---

## 🛠️ Architecture & Technology Stack
- **Visual Analytics Platform**: Tableau Desktop / Tableau Public (`banten_disaster_analysis_tableau.twb`).
- **Data Schemas & Storage Layer**: Relational multi-table Excel spreadsheets (`disaster_data_banten_tableau.xlsx`, `bencana_banten.xlsx`).
- **Analytical Metrics**: Calculated fields evaluating Disaster Incident Frequencies, Housing Structural Loss Index, and Human Casualty Densities.
- **Visual Design**: Choropleth geographic mapping, stacked damage severity bars, and coordinated cross-filtering matrices.

---

## 🔄 Methodology & Longitudinal Data Flow

```
Disparate Municipal Disaster Records (2021 - 2023)
├── Incident Frequency by Regency/Municipality
├── Residential Structural Damage (Severe, Moderate, Minor)
└── Human Casualties (Injuries, Fatalities, Evacuated Persons)
                            │
                            ▼
           Relational Data Cleaning & Union
                            │
                            ▼
   Tableau Dimensional Modeling (banten_disaster_analysis_tableau.twb)
   ├── Calculated Fields: Damage-to-Incident Ratios
   └── Geospatial Polygon Alignment (Banten Regencies)
                            │
                            ▼
   Interactive Multi-Tier Dashboard
   ├── Provincial Hazard Distribution Map
   ├── Longitudinal Trend Analysis (2021 vs 2022 vs 2023)
   └── Infrastructure Damage Severity Breakdown
```

---

## 📊 Key Dashboard Features & Empirical Insights
- **Geographic Vulnerability Epicenter**: Spatial mapping reveals that **Lebak and Pandeglang** regencies consistently experience over 60% of total province-wide hydrometeorological disaster occurrences and rural residential destruction.
- **Infrastructural Damage Grading**: Separates structural damage into standardized categories (*Rusak Berat, Rusak Sedang, Rusak Ringan*), highlighting that unreinforced rural masonry homes suffer disproportionately higher catastrophic collapse during flash floods.
- **Seasonal Surge Alignment**: Longitudinal time-series curves demonstrate significant disaster volume spikes aligned with the annual peak monsoon corridor (November through February), validating early-warning shelter prep timetables.
- **Coordinated Dynamic Filtering**: Selecting any specific hazard category (e.g., Landslide vs. Flood) instantly updates provincial casualty rankings, affected households, and district loss summaries.

---

## 🚀 How to Run & Explore

### 1. Requirements
Install [Tableau Desktop](https://www.tableau.com/products/desktop) (v2020.2 or newer) or [Tableau Reader](https://www.tableau.com/products/reader).

### 2. Launch Workbook
Open `banten_disaster_analysis_tableau.twb` directly. The workbook will automatically establish links with the underlying `disaster_data_banten_tableau.xlsx` and `bencana_banten.xlsx` datasets.

---

## 🖼️ Dashboard Interface & Spatial Risk Mapping
![Project Preview](./preview.png)
