import pandas as pd
from sqlalchemy import create_engine

# 1. Load the data we found in Step 1
try:
    df = pd.read_csv("delhi_stations_catalog.csv")
    print(f"📖 Loaded {len(df)} stations from CSV.")
except FileNotFoundError:
    print("❌ Error: 'delhi_stations_catalog.csv' not found. Run find_stations.py first!")
    exit()

# 2. Connection Settings
# We use the IP that worked for you previously
WINDOWS_IP = "172.21.160.1"
DB_NAME = "delhi_aqi_db"
DB_USER = "postgres"
DB_PASS = "Kush1909"  # <--- Change this to your real password

# 3. Create the Database Bridge
# Format: postgresql://user:password@host:port/database
connection_url = f"postgresql://{DB_USER}:{DB_PASS}@{WINDOWS_IP}:5432/{DB_NAME}"
engine = create_engine(connection_url)

# 4. Pour the data into SQL
try:
    print(f"🚀 Connecting to Windows PostgreSQL at {WINDOWS_IP}...")
    
    # This creates a table named 'delhi_stations' inside 'delhi_aqi_db'
    # 'replace' ensures that if you run it again, it refreshes the data
    df.to_sql('delhi_stations', engine, if_exists='replace', index=False)
    
    print("✅ SUCCESS! Your 71 stations are now stored in 'delhi_aqi_db'.")
    print("📂 Table Name: delhi_stations")

except Exception as e:
    print(f"❌ Connection Failed: {e}")
    print("\n💡 TIP: If it still says 'database does not exist', make sure you ran create_db.py first!")