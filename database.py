import sqlite3
import datetime
import hashlib

DB_NAME = "farm_data.db"

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # Users table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            location TEXT NOT NULL
        )
    ''')
    
    # Financial tracking with user_id
    c.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            category TEXT NOT NULL,
            amount REAL NOT NULL,
            date TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    # Smart advisor history with user_id
    c.execute('''
        CREATE TABLE IF NOT EXISTS soil_tests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            n INTEGER,
            p INTEGER,
            k INTEGER,
            ph REAL,
            rain REAL,
            temp REAL,
            crop TEXT,
            confidence REAL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    conn.commit()
    conn.close()

def register_user(username, password, location):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (username, password, location) VALUES (?, ?, ?)", 
                  (username, hash_password(password), location))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False # Username taken
    finally:
        conn.close()

def verify_login(username, password):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT id, location FROM users WHERE username = ? AND password = ?", 
              (username, hash_password(password)))
    user = c.fetchone()
    conn.close()
    if user:
        return {"id": user[0], "location": user[1]}
    return None

def add_expense(user_id, category, amount, date_str):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO expenses (user_id, category, amount, date) VALUES (?, ?, ?, ?)", 
              (user_id, category, amount, date_str))
    conn.commit()
    conn.close()

def get_expenses(user_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT category, amount, date FROM expenses WHERE user_id = ? ORDER BY date ASC", (user_id,))
    rows = c.fetchall()
    conn.close()
    return rows

def add_soil_test(user_id, date_str, n, p, k, ph, rain, temp, crop, confidence):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        INSERT INTO soil_tests (user_id, date, n, p, k, ph, rain, temp, crop, confidence)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (user_id, date_str, n, p, k, ph, rain, temp, crop, confidence))
    conn.commit()
    conn.close()

def get_latest_soil_test(user_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT date, crop, confidence FROM soil_tests WHERE user_id = ? ORDER BY id DESC LIMIT 1", (user_id,))
    row = c.fetchone()
    conn.close()
    return row

def get_all_soil_tests(user_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT date, crop, confidence FROM soil_tests WHERE user_id = ? ORDER BY id ASC", (user_id,))
    rows = c.fetchall()
    conn.close()
    return rows

init_db()
