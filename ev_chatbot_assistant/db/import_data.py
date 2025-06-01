import os
import pandas as pd
from sqlalchemy import create_engine

# Local DB URL for MacBook setup
DATABASE_URL = "postgresql+psycopg2://localhost/datakrew_db"

DATA_FOLDER = "./data"
engine = create_engine(DATABASE_URL)

TABLES = [
    "fleets", "vehicles", "raw_telemetry", "processed_metrics",
    "charging_sessions", "trips", "alerts", "battery_cycles",
    "maintenance_logs", "drivers", "driver_trip_map",
    "geofence_events", "fleet_daily_summary"
]

def load_csv(table):
    file_path = os.path.join(DATA_FOLDER, f"{table}.csv")
    print(f"Loading {file_path}")
    df = pd.read_csv(file_path)
    df.to_sql(table, engine, index=False, if_exists='append')
    print(f"✓ {len(df)} rows inserted into {table}")

if __name__ == "__main__":
    for table in TABLES:
        load_csv(table)

