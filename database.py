"""
Database Management - V2V 5G Platform
WORKS WITHOUT BCRYPT - Uses hashlib only
"""
import sqlite3
import os
import json
import hashlib
from datetime import datetime

# Database path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, '..', 'data')
DATABASE_PATH = os.path.join(DATA_DIR, 'simulator.db')

def hash_password(password):
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def verify_password(password, hashed):
    """Verify password against hash"""
    return hashlib.sha256(password.encode('utf-8')).hexdigest() == hashed

def get_db_connection():
    """Get database connection"""
    os.makedirs(DATA_DIR, exist_ok=True)
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    """Initialize database tables"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            nim TEXT PRIMARY KEY,
            password_hash TEXT NOT NULL,
            name TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Simulation history table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS simulation_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nim TEXT NOT NULL,
            experiment_id TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            num_vehicles INTEGER,
            num_platoons INTEGER,
            initial_spacing REAL,
            desired_speed REAL,
            latency_ms REAL,
            packet_loss REAL,
            network_slicing TEXT,
            collision_occurred INTEGER,
            duration_seconds REAL,
            avg_spacing_error REAL,
            final_stability REAL,
            config_json TEXT,
            results_json TEXT,
            FOREIGN KEY (nim) REFERENCES users(nim)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✓ Database initialized:", DATABASE_PATH)

def seed_users():
    """Seed default users"""
    users = [
        ('1101223157', '1101223157', 'Mahendra Aryaputra Fitrianto'),
        ('1101223332', '1101223332', 'Muhammad Abduh'),
        ('1101223172', '1101223172', 'Ahmad Zulfikar')
    ]
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    for nim, password, name in users:
        cursor.execute('SELECT nim FROM users WHERE nim = ?', (nim,))
        if cursor.fetchone() is None:
            password_hash = hash_password(password)
            cursor.execute(
                'INSERT INTO users (nim, password_hash, name) VALUES (?, ?, ?)',
                (nim, password_hash, name)
            )
            print(f"✓ Created user: {nim}")
    
    conn.commit()
    conn.close()

def verify_user(nim, password):
    """Verify user credentials"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT password_hash, name FROM users WHERE nim = ?', (nim,))
    result = cursor.fetchone()
    conn.close()
    
    if result:
        stored_hash = result['password_hash']
        name = result['name']
        if verify_password(password, stored_hash):
            return {'nim': nim, 'name': name}
    
    return None

def get_user_name(nim):
    """Get user name by NIM"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT name FROM users WHERE nim = ?', (nim,))
    result = cursor.fetchone()
    conn.close()
    
    return result['name'] if result else None

def save_simulation(nim, experiment_id, config, results):
    """Save simulation results to database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO simulation_history (
            nim, experiment_id, num_vehicles, num_platoons,
            initial_spacing, desired_speed, latency_ms, packet_loss,
            network_slicing, collision_occurred, duration_seconds,
            avg_spacing_error, final_stability, config_json, results_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        nim,
        experiment_id,
        config.get('num_vehicles', 0),
        config.get('num_platoons', 1),
        config.get('initial_spacing', 0),
        config.get('desired_speed', 0),
        config.get('latency_ms', 0),
        config.get('packet_loss', 0),
        config.get('network_slicing', 'URLLC'),
        1 if results.get('collision_occurred', False) else 0,
        results.get('duration', 0),
        results.get('avg_spacing_error', 0),
        results.get('final_stability', 0),
        json.dumps(config),
        json.dumps(results)
    ))
    
    conn.commit()
    conn.close()
    print(f"✓ Saved simulation: {experiment_id[:20]}...")

def get_user_history(nim):
    """Get simulation history for user"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM simulation_history
        WHERE nim = ?
        ORDER BY timestamp DESC
    ''', (nim,))
    
    results = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in results]

def get_simulation_detail(sim_id, nim):
    """Get specific simulation details"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM simulation_history
        WHERE id = ? AND nim = ?
    ''', (sim_id, nim))
    
    result = cursor.fetchone()
    conn.close()
    
    return dict(result) if result else None

# Initialize on import
if __name__ != '__main__':
    try:
        init_database()
        seed_users()
    except Exception as e:
        print(f"⚠ Database init warning: {e}")
