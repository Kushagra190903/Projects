import psycopg2
from sqlalchemy import create_engine, text

# Database Connection
DB_URL = "postgresql://postgres:Kush1909@172.21.160.1:5432/delhi_aqi_db"

def prepare_db():
    try:
        engine = create_engine(DB_URL)
        print("Connecting to database...")
        
        with engine.connect() as conn:
            print("Creating view 'delhi_aqi_daily'...")
            conn.execute(text("""
                CREATE OR REPLACE VIEW delhi_aqi_daily AS
                SELECT
                    station_name,
                    DATE(measurement_period) AS day,
                    AVG(aqi_value) AS daily_aqi,
                    COUNT(*) AS observations
                FROM city_stats_aqi_raw
                GROUP BY station_name, DATE(measurement_period);
            """))
            conn.commit() # Ensure commit for DDL in some configurations, though auto-commit might be on
            
            # Validation
            count = conn.execute(text("SELECT COUNT(*) FROM delhi_aqi_daily")).scalar()
            print(f"✅ View created. Total daily records: {count:,}")
            
            date_range = conn.execute(text("SELECT MIN(day), MAX(day) FROM delhi_aqi_daily")).fetchone()
            print(f"📅 Date Range: {date_range[0]} to {date_range[1]}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    prepare_db()
