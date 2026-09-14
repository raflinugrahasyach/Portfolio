# 🌶️ Agricultural Yield Forecasting: Multiple Linear Regression & Time Series (Streamlit App)

## 📖 Overview & Agronomic Impact
Extreme volatility in staple agricultural commodities—particularly perishables such as chili peppers—remains a major catalyst of regional food price inflation and supply chain disruption in developing agricultural economies. Farmers, commercial distributors, and policymakers require quantitative forecasting tools to anticipate harvest volume shortfalls months in advance.

This project delivers an end-to-end predictive decision support tool built with **Streamlit**. The application models and forecasts monthly chili harvest yields across two key production regions in East Java, Indonesia (**Malang** and **Lumajang**) by analyzing historical agronomic, meteorological, and land-use determinants: **precipitation levels**, **ambient temperature**, and **harvested acreage**.

---

## 📊 Dataset & Agronomic Predictors
The empirical foundation comprises 5 years of consolidated monthly time series records (2018–2022) compiled in `Data_Malang_Lumajang.xlsx`:

| Variable | Indicator | Unit | Agronomic Significance |
|----------|-----------|------|------------------------|
| **$X_1$** | Monthly Rainfall | mm/month | Soil moisture index & fungal risk factor |
| **$X_2$** | Ambient Temperature | °C (Mean) | Flowering, pollination, and fruit-set rate |
| **$X_3$** | Harvested Land Area | Hectares | Gross physical production capacity |
| **$Y$** | Harvest Yield (Target) | Metric Tons | Total realized monthly regional yield |

### Feature Engineering & Statistical Diagnostics:
- **Z-Score Normalization (`StandardScaler`)**: Mitigates magnitude distortion between land areas (hundreds of hectares) and ambient temperatures (~25–30°C), ensuring balanced parameter regression estimation.
- **Multicollinearity Screening**: Evaluated Variance Inflation Factors (VIF) to detect cross-correlation between climatic variables before parameter fitting.
- **Residual Normality & Homoscedasticity**: Verified via Q-Q residual plots to ensure valid OLS hypothesis testing.

---

## 🧠 Model Architecture & Analytics Workflow
The application implements two complementary modeling methodologies:

1. **Multiple Linear Regression (OLS)**:
   - Formulates the linear equation: $\hat{Y} = \beta_0 + \beta_1 X_1 + \beta_2 X_2 + \beta_3 X_3$.
   - Provides fully interpretable coefficients, standard errors, $t$-statistics, and $p$-values to help agricultural officers assess the marginal impact of weather deviations.
2. **Integrated Time-Series Forecasting (ARIMA / Moving Average)**:
   - Incorporates auto-regressive moving average models for weekly and monthly time-trend extrapolation, supporting proactive logistics planning.

---

## 📊 Key Results & Model Performance
- **Coefficient Analysis**: Harvested land area ($X_3$) accounts for the largest positive elasticity, while excessive precipitation ($X_1$) past regional saturation thresholds exhibits diminishing marginal yield returns due to root-rot vulnerability.
- **Statistical Fit**: Evaluated via Coefficient of Determination ($R^2$), Mean Absolute Error (MAE), and Root Mean Squared Error (RMSE) displayed dynamically within the dashboard.

---

## 🚀 How to Run the Streamlit Application

### 1. Install Dependencies
```bash
pip install streamlit pandas numpy matplotlib seaborn scikit-learn statsmodels openpyxl
```

### 2. Launch Streamlit Dashboard
```bash
streamlit run app.py
```

### 3. Interactive Web Workflow
Upload the historical dataset (`Data_Malang_Lumajang.xlsx` or custom `.xlsx` time-series files) to generate automated exploratory trend plots, compute regression fits, and simulate hypothetical weather and land scenarios.

---

## 🖼️ Application Interface & Regression Fit
![Project Preview](./preview.png)
