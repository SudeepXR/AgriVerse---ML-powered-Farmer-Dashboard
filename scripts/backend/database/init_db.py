import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "agriculture.db")

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# ================= FARMERS =================
cursor.execute("""
CREATE TABLE IF NOT EXISTS farmers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,

    full_name TEXT,
    phone TEXT,
    email TEXT,

    village TEXT NOT NULL,
    district TEXT NOT NULL,
    state TEXT DEFAULT 'Karnataka',

    latitude REAL,
    longitude REAL,

    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_login DATETIME,
    is_active INTEGER DEFAULT 1
);
""")

# ================= FARMER CROPS =================
cursor.execute("""
CREATE TABLE IF NOT EXISTS farmer_crops (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    farmer_id INTEGER NOT NULL,

    crop_name TEXT NOT NULL,
    season TEXT,
    area_acres REAL,

    sowing_date DATE,
    expected_harvest DATE,

    is_active INTEGER DEFAULT 1,

    FOREIGN KEY (farmer_id) REFERENCES farmers(id)
);
""")

# ================= SOIL REPORTS =================
cursor.execute("""
CREATE TABLE IF NOT EXISTS soil_reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    farmer_id INTEGER NOT NULL,

    nitrogen REAL NOT NULL,
    phosphorus REAL NOT NULL,
    potassium REAL NOT NULL,

    ph REAL,
    temperature REAL,
    humidity REAL,
    rainfall REAL,

    soil_health_score INTEGER,
    confidence_percentage INTEGER,

    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (farmer_id) REFERENCES farmers(id)
);
""")

# ================= DISEASE REPORTS =================
cursor.execute("""
CREATE TABLE IF NOT EXISTS disease_reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    farmer_id INTEGER NOT NULL,

    crop_name TEXT,
    disease_name TEXT,
    severity TEXT,

    image_path TEXT,
    ai_advice TEXT,

    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (farmer_id) REFERENCES farmers(id)
);
""")

# ================= FARMER HEADS =================
cursor.execute("""
CREATE TABLE IF NOT EXISTS farmer_heads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,

    full_name TEXT,
    role TEXT DEFAULT 'head',

    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_login DATETIME,
    is_active INTEGER DEFAULT 1
);
""")

# ================= ACCESS CONTROL =================
cursor.execute("""
CREATE TABLE IF NOT EXISTS farmer_access (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    head_id INTEGER NOT NULL,
    farmer_id INTEGER NOT NULL,

    can_view_soil INTEGER DEFAULT 1,
    can_view_crops INTEGER DEFAULT 1,
    can_view_disease INTEGER DEFAULT 1,

    granted_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(head_id, farmer_id),

    FOREIGN KEY (head_id) REFERENCES farmer_heads(id),
    FOREIGN KEY (farmer_id) REFERENCES farmers(id)
);
""")

conn.commit()
conn.close()

print("✅ Database and tables created successfully.")
