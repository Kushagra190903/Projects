import os
import json
import ppt_utils
import analysis_logic
from datetime import datetime

# Setup
OUTPUT_REPORT_DIR = "outputs/reports"
LOG_FILE = os.path.join(OUTPUT_REPORT_DIR, "run_log.txt")
SUMMARY_FILE = os.path.join(OUTPUT_REPORT_DIR, "executive_summary.txt")
METRICS_FILE = os.path.join(OUTPUT_REPORT_DIR, "summary_metrics.json")

def log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{timestamp}] {message}"
    print(entry)
    with open(LOG_FILE, "a") as f:
        f.write(entry + "\n")

def main():
    # Ensure directories
    os.makedirs(OUTPUT_REPORT_DIR, exist_ok=True)
    
    log("Starting Delhi AQI Structural Analysis...")
    
    # 1. Initialize Presentation
    prs = ppt_utils.create_presentation()
    log("Initialized PowerPoint presentation.")
    
    analysis_results = {}
    
    # 2. Phase 1: Dataset Understanding
    log("Running Phase 1: Dataset Understanding...")
    metrics, interp, plot = analysis_logic.analyze_dataset_understanding()
    ppt_utils.add_analysis_slide(prs, "Phase 1: Dataset Completeness", metrics, interp, plot)
    analysis_results['phase1'] = {'metrics': metrics, 'interpretation': interp}
    
    # 3. Phase 2: Structural Analyses
    
    # Analysis 1: Spatial Inequality
    log("Running Analysis 1: Spatial Inequality...")
    metrics, interp, plot = analysis_logic.analyze_spatial_inequality()
    ppt_utils.add_analysis_slide(prs, "1. Spatial Inequality of AQI", metrics, interp, plot)
    analysis_results['spatial'] = metrics
    
    # Analysis 2: Persistence
    log("Running Analysis 2: Persistence vs Episodic...")
    metrics, interp, plot = analysis_logic.analyze_persistence()
    ppt_utils.add_analysis_slide(prs, "2. Persistence vs Episodic Pollution", metrics, interp, plot)
    
    # Analysis 3: Seasonality
    log("Running Analysis 3: Seasonal Regimes...")
    metrics, interp, plot = analysis_logic.analyze_seasonality()
    ppt_utils.add_analysis_slide(prs, "3. Seasonal Regime Structure", metrics, interp, plot)
    
    # Analysis 4: Rank Stability
    log("Running Analysis 4: Rank Stability...")
    metrics, interp, plot = analysis_logic.analyze_rank_stability()
    ppt_utils.add_analysis_slide(prs, "4. Temporal Stability of Station Ranking", metrics, interp, plot)
    
    # Analysis 5: Extremes
    log("Running Analysis 5: Extreme Events...")
    metrics, interp, plot = analysis_logic.analyze_extremes()
    ppt_utils.add_analysis_slide(prs, "5. Concentration of Extreme Events", metrics, interp, plot)
    analysis_results['extremes'] = metrics
    
    # Analysis 6: Diurnal
    log("Running Analysis 6: Diurnal Cycle (2022)...")
    metrics, interp, plot = analysis_logic.analyze_diurnal()
    ppt_utils.add_analysis_slide(prs, "6. Representative Diurnal Cycle", metrics, interp, plot)
    
    # Analysis 7: Completeness (Robustness)
    log("Running Analysis 7: Data Completeness Robustness...")
    metrics, interp, plot = analysis_logic.analyze_completeness()
    ppt_utils.add_analysis_slide(prs, "7. Data Completeness Robustness", metrics, interp, plot)
    
    # Analysis 8: Synchronization
    log("Running Analysis 8: City-wide Synchronization...")
    metrics, interp, plot = analysis_logic.analyze_synchronization()
    ppt_utils.add_analysis_slide(prs, "8. City-wide Synchronization", metrics, interp, plot)
    
    # Analysis 9: Drift
    log("Running Analysis 9: Long-term Drift...")
    metrics, interp, plot = analysis_logic.analyze_drift()
    ppt_utils.add_analysis_slide(prs, "9. Long-term Drift vs Seasonality", metrics, interp, plot)
    
    # 4. Phase 3: Synthesis
    log("Generatings Synthesis...")
    
    synthesis_text = (
        "1. **Spatial Structure**: Distinct hotspots exist with high persistence.\n"
        "2. **Temporal Structure**: Seasonality is the dominant driver of variance.\n"
        "3. **Network Dynamics**: High city-wide synchronization suggests regional meteorological forcing.\n"
        "4. **Long-term**: No clear linear downtrend; inter-annual variability is high."
    )
    ppt_utils.add_analysis_slide(prs, "Synthesis & Interpretation", "", synthesis_text, None)
    
    # 5. Save PPT
    ppt_path = ppt_utils.save_presentation(prs)
    log(f"Saved Presentation to: {ppt_path}")
    
    # 6. Executive Outputs
    with open(SUMMARY_FILE, "w") as f:
        f.write("EXECUTIVE SUMMARY: DELHI AQI STRUCTURAL ANALYSIS\n")
        f.write("================================================\n\n")
        f.write("Overview:\n")
        f.write("Analyzed daily AQI data from 2017-2023 across ~40 stations.\n")
        f.write("Goal: Characterize spatial, temporal, and network structure of pollution.\n\n")
        f.write("Key Findings:\n")
        f.write(synthesis_text + "\n\n")
        f.write("Generated Metrics:\n")
        f.write(json.dumps(analysis_results, indent=2))
        
    with open(METRICS_FILE, "w") as f:
        json.dump(analysis_results, f, indent=4)
        
    log("Analysis Complete. Outputs generated.")

if __name__ == "__main__":
    main()
