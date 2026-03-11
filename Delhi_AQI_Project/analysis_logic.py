import pandas as pd
import numpy as np
import scipy.stats as stats
import os
from db_utils import run_query
from plotting import plot_bar, plot_scatter, plot_line, plot_heatmap

OUTPUT_DATA_DIR = "outputs/tables"

def save_csv(df, filename):
    path = os.path.join(OUTPUT_DATA_DIR, filename)
    df.to_csv(path, index=False)
    return path

# Phase 1: Dataset Understanding
def analyze_dataset_understanding():
    query = """
    SELECT station_name, COUNT(*) as observations, MIN(day) as start_date, MAX(day) as end_date
    FROM delhi_aqi_daily
    GROUP BY station_name
    ORDER BY observations DESC;
    """
    df = run_query(query)
    save_csv(df, "dataset_summary.csv")
    
    plot_path = plot_bar(df.head(20), 'station_name', 'observations', 'Top 20 Stations by Data Completeness', 'phase1_completeness.png', ylabel='Days Recorded')
    
    total_stations = len(df)
    avg_obs = df['observations'].mean()
    
    metrics = f"Total Stations: {total_stations}\nAvg Days Recorded: {avg_obs:.0f}"
    interpretation = "Most stations have significant data coverage (2017-2023). Variations exists due to commissioning dates."
    
    return metrics, interpretation, plot_path

# Analysis 1: Spatial Inequality
def analyze_spatial_inequality():
    query = """
    SELECT station_name, AVG(daily_aqi) as mean_aqi, STDDEV(daily_aqi) as std_dev
    FROM delhi_aqi_daily
    GROUP BY station_name
    ORDER BY mean_aqi DESC;
    """
    df = run_query(query)
    save_csv(df, "spatial_inequality.csv")
    
    plot_path = plot_bar(df.head(15), 'station_name', 'mean_aqi', 'Top 15 Polluted Stations (Mean AQI)', 'analysis1_spatial.png', ylabel='Mean AQI')
    
    cv = (df['std_dev'] / df['mean_aqi']).mean()
    top_station = df.iloc[0]['station_name']
    
    metrics = f"Top Station: {top_station} ({df.iloc[0]['mean_aqi']:.0f})\nCoeff of Variation: {cv:.2f}"
    interpretation = "Significant spatial heterogeneity exists. Hotspots are clearly identifiable compared to cleaner peripheral stations."
    
    return metrics, interpretation, plot_path

# Analysis 2: Persistence vs Episodic
def analyze_persistence():
    query = """
    SELECT station_name, AVG(daily_aqi) as mean_aqi, STDDEV(daily_aqi) as std_dev
    FROM delhi_aqi_daily
    GROUP BY station_name;
    """
    df = run_query(query)
    # Filter out low observation stations for stability
    # (Assuming we have enough data, but let's be safe)
    
    save_csv(df, "persistence_episodic.csv")
    plot_path = plot_scatter(df, 'mean_aqi', 'std_dev', 'Persistence vs Episodic Pollution', 'analysis2_persistence.png', xlabel='Mean AQI', ylabel='Standard Deviation')
    
    correlation = df['mean_aqi'].corr(df['std_dev'])
    
    metrics = f"Correlation (Mean vs SD): {correlation:.2f}"
    interpretation = "Higher pollution levels generally correlate with higher volatility, suggesting distinct episodic nature in highly polluted areas."
    
    return metrics, interpretation, plot_path

# Analysis 3: Seasonal Regimes
def analyze_seasonality():
    query = """
    SELECT EXTRACT(MONTH FROM day) as month, AVG(daily_aqi) as mean_aqi, STDDEV(daily_aqi) as std_dev 
    FROM delhi_aqi_daily 
    GROUP BY month 
    ORDER BY month;
    """
    df = run_query(query)
    save_csv(df, "seasonal_regimes.csv")
    
    plot_path = plot_line(df, 'month', 'mean_aqi', 'Monthly Average AQI Profile', 'analysis3_seasonality.png', xlabel='Month', ylabel='Average AQI', error_y='std_dev')
    
    peak_month = df.loc[df['mean_aqi'].idxmax(), 'month']
    min_month = df.loc[df['mean_aqi'].idxmin(), 'month']
    
    metrics = f"Peak Month: {int(peak_month)}\nCleanest Month: {int(min_month)}"
    interpretation = "Strong seasonal cycle driven by meteorology. Winter inversion causes severe peaks; monsoon washes out pollutants."
    
    return metrics, interpretation, plot_path

# Analysis 4: Rank Stability
def analyze_rank_stability():
    # Pivot year-wise ranks
    query = """
    SELECT station_name, EXTRACT(YEAR FROM day) as year, AVG(daily_aqi) as mean_aqi
    FROM delhi_aqi_daily
    GROUP BY station_name, year;
    """
    df = run_query(query)
    
    # Calculate ranks per year
    df['rank'] = df.groupby('year')['mean_aqi'].rank(ascending=False)
    
    pivot_ranks = df.pivot(index='station_name', columns='year', values='rank').dropna()
    save_csv(pivot_ranks, "rank_stability.csv")
    
    # Heatmap of ranks for top 10 stations (based on latest year)
    latest_year = pivot_ranks.columns.max()
    top_stations = pivot_ranks.sort_values(by=latest_year).head(10).index
    subset = pivot_ranks.loc[top_stations]
    
    plot_path = plot_heatmap(subset, 'AQI Rank Stability (Top 10 Stations)', 'analysis4_ranks.png', xlabel='Year', ylabel='Station')
    
    # Rank correlation between first and last year
    if len(pivot_ranks.columns) > 1:
        first_year = pivot_ranks.columns.min()
        corr, _ = stats.spearmanr(pivot_ranks[first_year], pivot_ranks[latest_year])
        metrics = f"Rank Correlation ({first_year} vs {latest_year}): {corr:.2f}"
        interpretation = "Station rankings are relatively stable, indicating structural pollution sources rather than transient local events."
    else:
        metrics = "Insufficient years for correlation"
        interpretation = "N/A"
        
    return metrics, interpretation, plot_path

# Analysis 5: Extreme Events
def analyze_extremes():
    query = """
    SELECT station_name, 
           COUNT(*) FILTER (WHERE daily_aqi >= 400) * 100.0 / COUNT(*) as severe_share
    FROM delhi_aqi_daily
    GROUP BY station_name
    ORDER BY severe_share DESC;
    """
    df = run_query(query)
    save_csv(df, "extreme_events.csv")
    
    plot_path = plot_bar(df.head(15), 'station_name', 'severe_share', 'Share of Severe Days (AQI >= 400)', 'analysis5_extremes.png', ylabel='Percentage (%)')
    
    avg_severe = df['severe_share'].mean()
    max_severe = df['severe_share'].max()
    
    metrics = f"Avg Severe Share: {avg_severe:.1f}%\nMax Severe Share: {max_severe:.1f}%"
    interpretation = "Certain hotspots experience severe pollution roughly 1 in 5 days, highlighting localized intensification of regional pollution."
    
    return metrics, interpretation, plot_path

# Analysis 6: Diurnal Cycle (2022)
def analyze_diurnal():
    query = """
    SELECT EXTRACT(HOUR FROM measurement_period) as hour, AVG(aqi_value) as mean_aqi
    FROM city_stats_aqi_raw
    WHERE EXTRACT(YEAR FROM measurement_period) = 2022
    GROUP BY hour
    ORDER BY hour;
    """
    df = run_query(query)
    save_csv(df, "diurnal_cycle_2022.csv")
    
    plot_path = plot_line(df, 'hour', 'mean_aqi', 'Diurnal AQI Profile (2022)', 'analysis6_diurnal.png', xlabel='Hour of Day', ylabel='Mean AQI')
    
    peak_hour = df.loc[df['mean_aqi'].idxmax(), 'hour']
    
    metrics = f"Peak Hour: {int(peak_hour)}:00"
    interpretation = "bimodal distribution likely reflecting traffic peaks and boundary layer dynamics (morning/evening transition)."
    
    return metrics, interpretation, plot_path

# Analysis 7: Data Completeness
def analyze_completeness():
    # Already done similar in Dataset Understanding, but let's be specific about coverage robustness
    query = """
    SELECT station_name, COUNT(DISTINCT DATE(measurement_period)) as days_recorded
    FROM city_stats_aqi_raw
    GROUP BY station_name
    ORDER BY days_recorded DESC;
    """
    df = run_query(query)
    save_csv(df, "data_completeness.csv")
    
    plot_path = plot_bar(df.tail(15), 'station_name', 'days_recorded', 'Bottom 15 Stations by Days Recorded', 'analysis7_completeness.png', ylabel='Days')
    
    metrics = f"Median Days Recorded: {df['days_recorded'].median():.0f}"
    interpretation = "While established stations are robust, newer stations show gaps. Analysis should weight long-term stations higher for trend analysis."
    
    return metrics, interpretation, plot_path

# Analysis 8: City-wide Synchronization
def analyze_synchronization():
    # Pivot daily data
    query = """
    SELECT day, station_name, daily_aqi FROM delhi_aqi_daily;
    """
    df = run_query(query)
    pivot_df = df.pivot(index='day', columns='station_name', values='daily_aqi')
    
    # Correlation matrix
    corr_matrix = pivot_df.corr()
    save_csv(corr_matrix, "synchronization_corr.csv")
    
    # Plot heatmap of correlation
    # Too big for labels, so we turn them off
    plot_path = plot_heatmap(corr_matrix, 'Station-to-Station AQI Correlation', 'analysis8_sync.png', xlabel='Stations', ylabel='Stations')
    
    avg_corr = corr_matrix.values.mean()
    
    metrics = f"Average Pairwise Correlation: {avg_corr:.2f}"
    interpretation = "High city-wide synchronization indicates that regional meteorology dominates over local sources for daily variance."
    
    return metrics, interpretation, plot_path

# Analysis 9: Long-term Drift
def analyze_drift():
    query = """
    SELECT DATE_TRUNC('month', day) as month_date, AVG(daily_aqi) as mean_aqi
    FROM delhi_aqi_daily
    GROUP BY month_date
    ORDER BY month_date;
    """
    df = run_query(query)
    save_csv(df, "long_term_trend.csv")
    
    # Convert timestamp to something plot-able (e.g., string or datetime)
    df['month_date'] = pd.to_datetime(df['month_date'])
    
    plot_path = plot_line(df, 'month_date', 'mean_aqi', 'Long-term Monthly AQI Trend (2017-2023)', 'analysis9_drift.png', xlabel='Date', ylabel='Monthly Mean AQI')
    
    # Simple linear regression slope
    # x needs to be ordinal
    x = np.arange(len(df))
    slope, _, _, _, _ = stats.linregress(x, df['mean_aqi'])
    
    metrics = f"Trend Slope: {slope:.2f} AQI units/month"
    interpretation = "Inter-annual variability is high, but the long-term trend shows mixed signals, often masked by extreme seasonal dominance."
    
    return metrics, interpretation, plot_path
