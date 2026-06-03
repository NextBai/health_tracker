import sqlite3
import json
import os

DATABASE = 'instance/health_tracker.db'

def get_db():
    conn = sqlite3.connect(DATABASE, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    if not os.path.exists('instance'):
        os.makedirs('instance')
    conn = get_db()
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            height REAL,
            weight REAL,
            age INTEGER,
            gender TEXT,
            occupation TEXT
        )
    ''')
    
    # Posture Records table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS posture_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            metrics TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # BP Records table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bp_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            systolic INTEGER NOT NULL,
            diastolic INTEGER NOT NULL,
            heart_rate INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()

def get_user_by_username(username):
    conn = get_db()
    user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    conn.close()
    return dict(user) if user else None

def get_user_by_id(user_id):
    conn = get_db()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    return dict(user) if user else None

def create_user(username, password_hash, height, weight, age, gender, occupation):
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO users (username, password_hash, height, weight, age, gender, occupation)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (username, password_hash, height, weight, age, gender, occupation))
        conn.commit()
        user_id = cursor.lastrowid
    except sqlite3.IntegrityError:
        user_id = None
    finally:
        conn.close()
    return user_id

def add_posture_record(user_id, metrics_dict):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO posture_records (user_id, metrics)
        VALUES (?, ?)
    ''', (user_id, json.dumps(metrics_dict)))
    conn.commit()
    conn.close()

def add_bp_record(user_id, systolic, diastolic, heart_rate):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO bp_records (user_id, systolic, diastolic, heart_rate)
        VALUES (?, ?, ?, ?)
    ''', (user_id, systolic, diastolic, heart_rate))
    conn.commit()
    conn.close()

def get_recent_postures(user_id, limit=50):
    conn = get_db()
    records = conn.execute('''
        SELECT * FROM posture_records 
        WHERE user_id = ? 
        ORDER BY timestamp ASC LIMIT ?
    ''', (user_id, limit)).fetchall()
    conn.close()
    return [dict(r) for r in records]

def get_recent_bps(user_id, limit=50):
    conn = get_db()
    records = conn.execute('''
        SELECT * FROM bp_records 
        WHERE user_id = ? 
        ORDER BY timestamp ASC LIMIT ?
    ''', (user_id, limit)).fetchall()
    conn.close()
    return [dict(r) for r in records]
