import pandas as pd
from sqlalchemy import create_engine, text

# Database Configuration
# Host: 172.21.160.1, DB: delhi_aqi_db, User: postgres, Pass: Kush1909
DB_URL = "postgresql://postgres:Kush1909@172.21.160.1:5432/delhi_aqi_db"

def check_data():
    try:
        engine = create_engine(DB_URL)
        print(f"Connecting to database...")
        
        with engine.connect() as conn:
            # 1. Total Count
            count = conn.execute(text("SELECT count(*) FROM city_stats_aqi_raw")).scalar()
            print(f"\n✅ Total Rows in 'city_stats_aqi_raw': {count:,}")
            
            # 2. Distinct Stations
            stations = conn.execute(text("SELECT count(DISTINCT station_name) FROM city_stats_aqi_raw")).scalar()
            print(f"✅ Distinct Stations: {stations}")
            
            # 3. Sample Data
            print("\n🔍 Sample Data (Last 5 records):")
            df = pd.read_sql("SELECT * FROM city_stats_aqi_raw ORDER BY measurement_period DESC LIMIT 5", conn)
            print(df.to_string(index=False))
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_data()
