import pandas as pd
import requests
import time
from sqlalchemy import create_engine
from datetime import datetime, timedelta

# --- CONFIGURATION ---
API_KEY = "98d5e8bf9c21d15170c206962c48de1e71940e796176f442ba5ddee69b8750bc" 
DB_ENGINE = create_engine("postgresql://postgres:YOUR_PASSWORD@172.21.160.1:5432/delhi_aqi_db")

# Parameters to fetch (1=PM10, 2=PM2.5, 3=O3, 5=NO2, 7=CO, 8=SO2)
COMMON_PARAMS = [1, 2, 3, 5, 7, 8] 
headers = {"X-API-Key": API_KEY}

def download_all_history(loc_id, loc_name):
    print(f"\n🌍 STATION: {loc_name} (ID: {loc_id})")
    
    # Calculate date range (5 years back)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=5*365)

    # For each pollutant parameter...
    for p_id in COMMON_PARAMS:
        current_end = end_date
        print(f"  🔍 Checking Parameter ID: {p_id}...")

        while current_end > start_date:
            current_start = current_end - timedelta(days=60) # 60-day chunks
            
            url = f"https://api.openaq.org/v3/locations/{loc_id}/measurements"
            params = {
                "parameters_id": p_id,
                "date_from": current_start.strftime("%Y-%m-%d"),
                "date_to": current_end.strftime("%Y-%m-%d"),
                "limit": 1000
            }

            try:
                time.sleep(0.5)
                res = requests.get(url, params=params, headers=headers, timeout=30)
                
                if res.status_code == 200:
                    data = res.json().get('results', [])
                    if data:
                        batch = [{
                            'station_id': loc_id,
                            'parameter': r['parameter']['name'],
                            'value': r['value'],
                            'unit': r['parameter']['units'],
                            'timestamp_utc': r['period']['datetimeFrom']['utc']
                        } for r in data]
                        
                        pd.DataFrame(batch).to_sql('delhi_aqi_history', DB_ENGINE, if_exists='append', index=False)
                        print(f"    ✅ Saved {len(batch)} rows ({params['date_from']})")
                    else:
                        # If no data for this month, move back faster
                        pass 
                
                elif res.status_code == 429:
                    print("    ⏳ Rate limited. Waiting 30s...")
                    time.sleep(30)
                    continue

            except Exception as e:
                print(f"    ⚠️ Error: {e}. Retrying...")
                time.sleep(5)
                continue

            current_end = current_start

if __name__ == "__main__":
    # Get your list of 71 stations from the DB
    try:
        stations = pd.read_sql('SELECT "ID" as id, "Name" as name FROM delhi_stations', DB_ENGINE)
        for _, row in stations.iterrows():
            download_all_history(row['id'], row['name'])
    except Exception as e:
        print(f"❌ Startup Error: {e}")