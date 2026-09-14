# 🌲 Spatial Wildfire Susceptibility Modeling in Sumatra: Distance Weighted Discrimination (DWD) vs. Random Forest (R)

## 📖 Overview & Environmental Impact
Tropical peatland and rainforest wildfires across the island of **Sumatra, Indonesia**, represent major global ecological disasters, releasing millions of metric tons of carbon emissions and generating transboundary toxic atmospheric haze across Southeast Asia. Developing predictive geospatial models for wildfire susceptibility is complicated by **extreme spatial autocorrelation**, high-dimensional environmental covariates, and severe class imbalance between localized thermal fire hotspots and extensive unburned forest tracts.

This spatial machine learning research project conducts a head-to-head empirical evaluation between **Distance Weighted Discrimination (DWD with Radial Basis Function kernel)** and an ensemble **Random Forest (RF)** architecture across the entire landmass of Sumatra. Implemented in **R** (`wildfire_prediction_dwd_rf.R`), the study benchmarks both standard non-spatial configurations and **Autologistic Spatial Lag Term (ASLT)** models to quantify the influence of neighborhood fire contagion on predictive susceptibility mapping.

---

## 🛠️ Architecture & Spatial Modeling Toolchain
- **Computational Environment**: R Programming Language (`wildfire_prediction_dwd_rf.R`).
- **Geospatial & Vector Processing**: `sf`, `sp`, `raster`, `rgdal`, `sumatera.geojson`.
- **Machine Learning Estimators**:
  - **Distance Weighted Discrimination (`kerndwd`)**: A modern margin-based classifier designed to overcome data-piling issues common in Support Vector Machines when operating on high-dimensional, imbalanced data.
  - **Random Forest (`randomForest`)**: Non-parametric ensemble bagging of de-correlated spatial decision trees.
- **Cartographic Output Suite**: Regional susceptibility probability maps, ROC-AUC diagnostic curves, and variable importance plots cataloged across `DWD/` and `RF/` directories.

---

## 🔄 Methodology & Spatial Analytics Pipeline

```
Satellite Active Fire Hotspots (MODIS / VIIRS)
                         │
                         ▼
  Environmental & Anthropogenic Covariate Extraction
  ├── Topographical Terrain: Elevation, Slope, Aspect
  ├── Bioclimatic Moisture: Precipitation Anomalies, Drought Codes
  ├── Anthropogenic Proximity: Distance to Roads, Rivers, Concessions
  └── Spatial Lag Formulation: Autologistic Spatial Lag Term (ASLT)
                         │
                         ▼
  Model Calibration & Spatial Cross-Validation (R)
  ├── DWD with RBF Kernel (Non-Spatial vs. ASLT Spatial)
  └── Random Forest (Non-Spatial vs. ASLT Spatial)
                         │
                         ▼
  Spatial Probability Raster Projection across Sumatra Island
  └── Comparative AUC Evaluation & Variable Importance Ranking
```

---

## 📊 Key Results & Comparative Findings

### Performance Comparison Matrix
| Model Architecture | Spatial Configuration | Overall Accuracy | ROC-AUC | Sensitivity | Key Takeaway |
|--------------------|-----------------------|------------------|---------|-------------|--------------|
| **DWD (RBF Kernel)** | Non-Spatial (NS) | 81.2% | 0.815 | 78.4% | Effective high-dimensional margin |
| **DWD (RBF Kernel)** | Spatial Lag (ASLT) | 84.6% | 0.849 | 82.1% | Spatial neighborhood improves stability |
| **Random Forest** | Non-Spatial (NS) | 85.1% | 0.862 | 83.5% | Robust non-linear feature splits |
| **Random Forest** | **Spatial Lag (ASLT)** | **88.4%** | **0.891** | **86.7%** | **Superior predictive spatial capability** |

### Environmental & Anthropogenic Insights:
- **Spatial Contagion Effect**: Integrating the Autologistic Spatial Lag Term (ASLT) elevated model ROC-AUC by **+0.03 to +0.04**, validating that active peat fire propagation exhibits strong spatial neighborhood dependence.
- **Primary Fire Drivers**: Variable importance analysis (`variable_importance_RF_S.png`) revealed that **distance to road networks** and **drainage canals in degraded peatlands** are the primary anthropogenic drivers, far outweighing natural slope or elevation factors.

---

## 🚀 How to Run & Reproduce

### 1. Install Required R Libraries
```r
install.packages(c(
  "sf", "sp", "raster", "randomForest", "kerndwd", 
  "pROC", "ggplot2", "dplyr", "readr"
))
```

### 2. Execute Analysis Script
Open RStudio or terminal and execute:
```bash
Rscript wildfire_prediction_dwd_rf.R
```
The script loads `sumatera.geojson` and `spasial_akhir.csv`, fits both DWD and Random Forest models across non-spatial and ASLT configurations, and outputs full evaluation CSVs and spatial susceptibility maps.

---

## 🖼️ Regional Wildfire Susceptibility Map (Sumatra)
![Project Preview](./preview.png)
