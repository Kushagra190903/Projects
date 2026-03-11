import pandas as pd
import os
import re
import argparse
from datetime import datetime
from sqlalchemy import create_engine, text

# --- CONFIGURATION ---
DB_URL = "postgresql://postgres:Kush1909@172.21.160.1:5432/delhi_aqi_db"
DATA_DIR = "/home/kushdev/python_project/Delhi_AQI_Project/Aqi Data Delhi"

def get_db_engine():
    return create_engine(DB_URL)

def init_db(engine):
    """Creates the master table if it doesn't exist."""
    print("Initializing database...")
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS city_stats_aqi_raw (
                station_name VARCHAR(255) NOT NULL,
                measurement_period TIMESTAMP NOT NULL,
                aqi_value FLOAT,
                raw_filename VARCHAR(255),
                ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (station_name, measurement_period)
            );
        """))
        conn.commit()
    print("Database initialized.")

def parse_custom_csv(filepath, station_name, dry_run=False):
    """
    Parses complex CSV formats with repeating block headers and variable column offsets.
    Strategies:
    1. Detect Header Rows containing '00:00:00' to assume column mapping.
    2. Detect Year/Month context from any text line.
    3. Extract Day and Data based on detected offsets.
    """
    records = []
    
    current_year = None
    current_month_name = None
    
    # Indices determined dynamically
    data_start_idx = None # Index where 00:00 starts
    day_col_idx = None    # Index where Day (1-31) is located
    
    print(f"Parsing: {os.path.basename(filepath)}")
    
    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        lines = f.readlines()
        
    for line in lines:
        line = line.strip()
        if not line: continue
        
        parts = [p.strip() for p in line.split(',')]
        
        # --- Context Detection ---
        
        # 1. Year Detection
        # Check for explicitly labelled "Year" or "Year,2017" or inside cells
        # Some lines: "Year,2017" or "24,Year,2018..."
        for i, p in enumerate(parts):
            if 'year' in p.lower():
                # Check next col for year
                if i+1 < len(parts) and parts[i+1].isdigit() and len(parts[i+1]) == 4:
                    current_year = int(parts[i+1])
                    break
        
        # 2. Header Row Detection (Anchor for column structure)
        # Look for "00:00" or "00:00:00"
        if any('00:00' in p for p in parts):
            try:
                # Find index of 00:00
                dummy_idx = next(i for i, p in enumerate(parts) if '00:00' in p)
                data_start_idx = dummy_idx
                day_col_idx = dummy_idx - 1
                
                # Also check if this header row contains Month info
                # e.g. "January-2017,00:00..."
                for p in parts:
                    if '-' in p and any(m in p for m in ['January','February','March','April','May','June','July','August','September','October','November','December']):
                        m_parts = p.split('-')
                        current_month_name = m_parts[0]
                        if m_parts[1].isdigit():
                            current_year = int(m_parts[1])
            except:
                pass
            continue # Header row itself is not data
            
        # 3. Month Context (if not in header row, sometimes standalone)
        # Scan for Month strings
        for p in parts:
            if '-' in p:
                candidates = [m for m in ['January','February','March','April','May','June','July','August','September','October','November','December'] if m in p]
                if candidates:
                    m_parts = p.split('-')
                    current_month_name = m_parts[0]
                    if len(m_parts) > 1 and m_parts[1].isdigit():
                        current_year = int(m_parts[1])
                    break

        # --- Data Extraction ---
        if data_start_idx is None or day_col_idx is None:
            continue
            
        if not current_year or not current_month_name:
            continue
            
        # Ensure row has enough columns
        if len(parts) <= data_start_idx:
            continue
            
        # Extract Day
        day_str = parts[day_col_idx]
        if not day_str.isdigit():
            continue
            
        day = int(day_str)
        if day < 1 or day > 31:
            continue
            
        try:
            date_str = f"{day}-{current_month_name}-{current_year}"
            base_date = datetime.strptime(date_str, "%d-%B-%Y")
            
            # Extract 24 hourly values
            for hour in range(24):
                col = data_start_idx + hour
                if col < len(parts):
                    val_str = parts[col]
                    if val_str:
                        try:
                            val = float(val_str)
                            ts = base_date.replace(hour=hour, minute=0, second=0)
                            
                            records.append({
                                'station_name': station_name,
                                'measurement_period': ts,
                                'aqi_value': val,
                                'raw_filename': os.path.basename(filepath)
                            })
                        except ValueError:
                            pass
        except Exception:
            pass

    if dry_run:
        print(f"  -> Extracted {len(records)} records (Dry Run)")
        if records:
            print(f"  -> Sample: {records[0]}")
            print(f"  -> Sample: {records[-1]}")
    
    return records

def ingest_all(dry_run=False):
    engine = get_db_engine()
    if not dry_run:
        init_db(engine)
    
    files = [f for f in os.listdir(DATA_DIR) if f.endswith('.csv') and 'Zone.Identifier' not in f]
    
    total_records = 0
    
    for fname in files:
        fpath = os.path.join(DATA_DIR, fname)
        
        # Derive station name cleanly
        # e.g., "Alipur DPCC AQI Data 2017-2023.csv" -> "Alipur DPCC"
        # Removing "AQI Data 2017-2023.csv"
        clean_name = fname.replace(' AQI Data 2017-2023.csv', '').replace('.csv', '').strip()
        
        data = parse_custom_csv(fpath, clean_name, dry_run=dry_run)
        
        if not dry_run and data:
            df = pd.DataFrame(data)
            
            # Upsert strategy: Use pandas to_sql into temp table, then INSERT ON CONFLICT to main
            # Actually, for simplicity on this scale (3M rows), simple chunks might be okay but conflict handling is key.
            # We'll try direct to_sql chunks but we need handling for duplicates if re-run.
            # Efficient way:
            
            try:
                # Write to database (using 'append' might fail on PK constraint)
                # We will just iterate and insert with ON CONFLICT DO NOTHING natively or use simple "if exists append" relies on no constraints?
                # The user asked for safeguards.
                # Let's effectively filter duplicates or use a stronger method.
                # For this specific "bulk load" task, we can just use `to_sql` and manage exceptions? No, too slow.
                # Better: Write to temp table, then Insert Ignore.
                
                with engine.begin() as conn:
                   # Create temp table
                   conn.execute(text("CREATE TEMP TABLE tmp_aqi (LIKE city_stats_aqi_raw INCLUDING ALL)"))
                   
                   # Insert valid data to temp
                   df.to_sql('tmp_aqi', conn, if_exists='append', index=False)
                   
                   # Merge
                   conn.execute(text("""
                       INSERT INTO city_stats_aqi_raw 
                       SELECT * FROM tmp_aqi
                       ON CONFLICT (station_name, measurement_period) DO NOTHING
                   """))
                   
                   # Drop temp
                   conn.execute(text("DROP TABLE tmp_aqi"))
                
                print(f"  -> Ingested {len(df)} rows for {clean_name}")
                total_records += len(df)
                
            except Exception as e:
                print(f"  -> Failed to ingest {clean_name}: {e}")
                
    print(f"\nTotal Records Processed: {total_records}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Parse files but do not write to DB")
    args = parser.parse_args()
    
    ingest_all(dry_run=args.dry_run)
