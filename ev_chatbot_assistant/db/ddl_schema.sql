-- ENUM definitions
CREATE TYPE alert_severity AS ENUM ('low', 'medium', 'high');
CREATE TYPE soc_band_enum AS ENUM ('low', 'medium', 'high');

-- Fleets table
CREATE TABLE fleets (
    fleet_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    country VARCHAR(10),
    time_zone VARCHAR(50)
);

-- Vehicles table
CREATE TABLE vehicles (
    vehicle_id INTEGER PRIMARY KEY,
    vin VARCHAR(17) UNIQUE,
    fleet_id INTEGER REFERENCES fleets(fleet_id),
    model TEXT,
    make TEXT,
    variant TEXT,
    registration_no TEXT,
    purchase_date DATE
);

-- Raw telemetry table
CREATE TABLE raw_telemetry (
    ts TIMESTAMP,
    vehicle_id INTEGER REFERENCES vehicles(vehicle_id),
    soc_pct DECIMAL,
    pack_voltage_v DECIMAL,
    pack_current_a DECIMAL,
    batt_temp_c DECIMAL,
    latitude DECIMAL,
    longitude DECIMAL,
    speed_kph DECIMAL,
    odo_km DECIMAL,
    PRIMARY KEY (ts, vehicle_id)
);

-- Processed metrics table
CREATE TABLE processed_metrics (
    ts TIMESTAMP,
    vehicle_id INTEGER REFERENCES vehicles(vehicle_id),
    avg_speed_kph_15m DECIMAL,
    distance_km_15m DECIMAL,
    energy_kwh_15m DECIMAL,
    battery_health_pct DECIMAL,
    soc_band soc_band_enum,
    PRIMARY KEY (ts, vehicle_id)
);

-- Charging sessions table
CREATE TABLE charging_sessions (
    session_id SERIAL PRIMARY KEY,
    vehicle_id INTEGER REFERENCES vehicles(vehicle_id),
    start_ts TIMESTAMP,
    end_ts TIMESTAMP,
    start_soc DECIMAL,
    end_soc DECIMAL,
    energy_kwh DECIMAL,
    location TEXT
);

-- Trips table
CREATE TABLE trips (
    trip_id INTEGER PRIMARY KEY,
    vehicle_id INTEGER REFERENCES vehicles(vehicle_id),
    start_ts TIMESTAMP,
    end_ts TIMESTAMP,
    distance_km DECIMAL,
    energy_kwh DECIMAL,
    idle_minutes INTEGER,
    avg_temp_c DECIMAL
);

-- Alerts table
CREATE TABLE alerts (
    alert_id SERIAL PRIMARY KEY,
    vehicle_id INTEGER REFERENCES vehicles(vehicle_id),
    alert_type TEXT,
    severity alert_severity,
    alert_ts TIMESTAMP,
    value DECIMAL,
    threshold DECIMAL,
    resolved_bool BOOLEAN,
    resolved_ts TIMESTAMP
);

-- Battery cycles table
CREATE TABLE battery_cycles (
    cycle_id SERIAL PRIMARY KEY,
    vehicle_id INTEGER REFERENCES vehicles(vehicle_id),
    ts TIMESTAMP,
    dod_pct DECIMAL,
    soh_pct DECIMAL
);

-- Maintenance logs table
CREATE TABLE maintenance_logs (
    maint_id SERIAL PRIMARY KEY,
    vehicle_id INTEGER REFERENCES vehicles(vehicle_id),
    maint_type TEXT,
    start_ts TIMESTAMP,
    end_ts TIMESTAMP,
    cost_sgd DECIMAL,
    notes TEXT
);

-- Drivers table
CREATE TABLE drivers (
    driver_id INTEGER PRIMARY KEY,
    fleet_id INTEGER REFERENCES fleets(fleet_id),
    name TEXT,
    license_no TEXT,
    hire_date DATE
);

-- Driver-trip map table
CREATE TABLE driver_trip_map (
    trip_id INTEGER REFERENCES trips(trip_id),
    driver_id INTEGER REFERENCES drivers(driver_id),
    primary_bool BOOLEAN DEFAULT TRUE
);

-- Geofence events table
CREATE TABLE geofence_events (
    event_id SERIAL PRIMARY KEY,
    vehicle_id INTEGER REFERENCES vehicles(vehicle_id),
    geofence_name TEXT,
    enter_ts TIMESTAMP,
    exit_ts TIMESTAMP
);

-- Fleet daily summary table
CREATE TABLE fleet_daily_summary (
    fleet_id INTEGER REFERENCES fleets(fleet_id),
    date DATE,
    total_distance_km DECIMAL,
    total_energy_kwh DECIMAL,
    active_vehicles INTEGER,
    avg_soc_pct DECIMAL
);

