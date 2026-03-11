import pandas as pd
from sqlalchemy import create_engine, text

DB_URL = "postgresql://postgres:Kush1909@172.21.160.1:5432/delhi_aqi_db"

def get_engine():
    return create_engine(DB_URL)

def run_query(query):
    """Executes a SQL query and returns a pandas DataFrame."""
    engine = get_engine()
    with engine.connect() as conn:
        return pd.read_sql(query, conn)
