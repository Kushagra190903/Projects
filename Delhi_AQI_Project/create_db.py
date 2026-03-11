import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Connection details to the 'postgres' database (which we know works!)
WINDOWS_IP = "172.21.160.1"
DB_USER = "postgres"
DB_PASS = "Kush1909" 

def create_database():
    # Connect to the server's default DB
    con = psycopg2.connect(dbname='postgres', user=DB_USER, host=WINDOWS_IP, password=DB_PASS)
    con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT) # Required to create DBs
    cursor = con.cursor()
    
    try:
        # This is the magic command
        cursor.execute("CREATE DATABASE delhi_aqi_db")
        print("🛠️ Database 'delhi_aqi_db' created successfully!")
    except Exception as e:
        print(f"⚠️ Note: {e}")
    finally:
        cursor.close()
        con.close()

if __name__ == "__main__":
    create_database()