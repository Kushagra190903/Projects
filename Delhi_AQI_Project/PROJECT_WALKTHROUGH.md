# Delhi AQI Structural Analysis — Project Walkthrough

## 1. Executive Summary
This project successfully transformed raw, extensive air quality data into a structured research output. We ingested ~1.7 million hourly records from 38 monitoring stations in Delhi (2017–2023), aggregated them into a clean daily analytical dataset, and performed nine targeted structural analyses. The study reveals that Delhi’s pollution is **structurally rigid** (hotspots persist year-round), **seasonally dominated** (winter meteorology forces city-wide peaks), and **highly synchronized** (the city acts as a single airshed). Statistical tests confirm no significant long-term linear trend (p=0.74), suggesting that policy interventions are currently competing with, and often masked by, meteorological variability.

---

## 2. Phase-Wise Explanation

### PHASE 0 — Data Ingestion & Preparation
*   **Goal**: Create a reliable SQL backend from raw CSVs.
*   **Action**: Ingested ~78 CSV files using a custom parser to handle variable column formats. Created a unified PostgreSQL table `city_stats_aqi_raw`.
*   **Validation**: 1,725,370 rows ingested. `prepare_db.py` created the `delhi_aqi_daily` view for analysis.
*   **Key File**: `db_utils.py`, `prepare_db.py`

### PHASE 1 — Daily AQI Dataset Construction
*   **Goal**: Validate data completeness before analysis.
*   **Action**: Aggregated hourly data to daily means. Assessed station coverage.
*   **Result**: 38 stations with >2000 recorded days on average. Core network is robust.
*   **Evidence**: `outputs/plots/phase1_completeness.png`, `outputs/tables/dataset_summary.csv`

### PHASE 2 — Structural Analyses (1–9)
We executed nine distinct analytical modules. All outputs are in `outputs/plots/` and `outputs/tables/`.

**1. Spatial Inequality**
*   **Method**: Mean station comparison.
*   **Result**: Anand Vihar (Mean AQI ~260) vs cleaner periphery. CV = 0.52.
*   **Meaning**: Where you live determines your baseline exposure.

**2. Persistence vs Episodic**
*   **Method**: Mean vs SD scatter plot.
*   **Result**: Positive correlation.
*   **Meaning**: Dirtier stations are also more volatile; they suffer from extreme spikes, not just high baselines.

**3. Seasonal Regimes**
*   **Method**: Monthly mean aggregation.
*   **Result**: Winter (Dec/Jan) AQI is 3-4x higher than Monsoon (Aug).
*   **Meaning**: Meteorology (inversion layers) is the primary driver of variance.

**4. Rank Stability**
*   **Method**: Spearman Rank Correlation of stations year-over-year.
*   **Result**: Avg Correlation = 0.69.
*   **Meaning**: The "clean" and "dirty" areas remain the same every year. Sources are structural.

**5. Extreme Events**
*   **Method**: Frequency of AQI ≥ 400 (Severe).
*   **Result**: Hotspots face "Severe" air ~14.5% of the time.
*   **Meaning**: Extreme events are concentrated, creating zones of hazardous health burden.

**6. Diurnal Cycle**
*   **Method**: Hourly aggregation (2022).
*   **Result**: Bimodal peaks (Morning rush / Evening PBL collapse).
*   **Meaning**: Traffic emissions + boundary layer dynamics drive daily rhythm.

**7. Data Completeness**
*   **Method**: Daily count check.
*   **Result**: Core stations >90% coverage.
*   **Meaning**: Long-term trend analysis is statistically valid on the core network.

**8. City-wide Synchronization**
*   **Method**: Pairwise correlation matrix.
*   **Result**: Mean off-diagonal correlation = 0.90.
*   **Meaning**: The city breathes as one. When one station is high, they are all high.

**9. Long-term Drift**
*   **Method**: Mann-Kendall Trend Test on monthly means.
*   **Result**: p=0.74 (No significant trend).
*   **Meaning**: Inter-annual weather noise masks any gradual policy improvements.

### PHASE 3 — Cross-Analysis Synthesis
*   **Action**: Integrated findings into a narrative.
*   **Finding**: The combination of High Synchronization (Analysis 8) and Seasonal Dominance (Analysis 3) proves that **Regional Meteorology > Local Sources** for day-to-day variance.
*   **Evidence**: `outputs/reports/executive_summary.txt`

### PHASE 4 — Deliverables
*   **Action**: Generated professional PowerPoint.
*   **Result**: Valid, binary PPTX with 10 slides.
*   **Evidence**: `outputs/presentation/Delhi_AQI_Structural_Analysis.pptx`

---

## 3. Key Quantitative Findings

| Metric | Value | Interpretation |
| :--- | :--- | :--- |
| **Stations** | 38 | Robust spatial coverage |
| **Max Mean AQI** | ~260 (Anand Vihar) | Persistent hotspot |
| **Spatial Coeff. Var.** | 0.52 | Significant spatial inequality |
| **Severe Days Share** | 14.5% (Max) | High burden of extremes |
| **Rank Correlation** | 0.69 | Hotspots don't shift |
| **Synchronization** | 0.90 | Regional unity |
| **Trend Test (p)** | 0.74 | No linear trend detected |

---

## 4. Scientific Conclusions
1.  **Structural Rigidity**: Pollution sources are not transient. The same locations are polluted year after year (High Rank Stability).
2.  **Meteorological Tyranny**: The massive seasonal swing and high synchronization prove that weather conditions (boundary layer, wind speed) are the dominant amplifier of pollution.
3.  **Single Airshed**: Delhi cannot be managed zone-by-zone. The sheer synchronicity (0.90 correlation) demands a region-wide airshed management strategy.

---

## 5. Limitations
*   **Composite Metric**: AQI combines PM10, PM2.5, NO2, etc. Trends in PM2.5 might differ from PM10 but are masked by the aggregate index.
*   **No Weather Normalization**: We did not "de-weather" the data. We cannot say emissions haven't dropped; we can only say observed concentrations haven't dropped.
*   **Spatial Gaps**: Western and Northern peripheries have fewer sensors than Central/South Delhi.

---

## 6.  Next Research Steps
1.  **Pollutant Isolation**: Re-run Analysis 9 (Time Series) specifically on PM2.5.
2.  **Meteorological Normalization**: Use Random Forest or GAMs to regress AQI against wind speed/temperature to isolate the "emissions" signal.
3.  **Episode Analysis**: Investigate the specific dates of the "Severe" days to categorize them by cause (e.g., crop burning vs Diwali vs stillness).

---



And third, **Synchronization**. I found a city-wide correlation of 0.90. This is extremely high. It means the entire city acts as a single airshed. When pollution spikes, it spikes everywhere simultaneously.

Finally, I tested for long-term trends using the Mann-Kendall test. The result was 'No Significant Trend' (p=0.74). This suggests that while we see year-to-year variation, there is no statistically significant linear decline in aggregate AQI over this 7-year period, likely because extreme weather masks policy gains.

I have summarized these findings in a polished PowerPoint presentation and a full executive report."
