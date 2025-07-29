import sqlite3
from datetime import datetime, timedelta

DB_NAME = 'noninventory.db'


def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            partNumber TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            value REAL NOT NULL,
            added_date TEXT NOT NULL,
            expiry_days INTEGER NOT NULL
        )
    ''')
    conn.commit()
    conn.close()


def get_items():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM items")
    rows = cursor.fetchall()
    conn.close()
    return rows


def add_item(partNumber, quantity, value, expiry_days):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO items (partNumber, quantity, value, added_date, expiry_days)
        VALUES (?, ?, ?, ?, ?)
    ''', (partNumber, quantity, value, datetime.now().isoformat(), expiry_days))
    conn.commit()
    conn.close()


def update_item(item_id, partNumber, quantity, value, expiry_days):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE items
        SET partNumber=?, quantity=?, value=?, expiry_days=?
        WHERE id=?
    ''', (partNumber, quantity, value, expiry_days, item_id))
    conn.commit()
    conn.close()


def delete_item(item_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM items WHERE id=?", (item_id,))
    conn.commit()
    conn.close()


def get_expiring_items():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    now = datetime.now()
    cursor.execute('SELECT * FROM items')
    rows = cursor.fetchall()
    conn.close()

    expiring = []
    for row in rows:
        added_date = datetime.fromisoformat(row[4])
        expiry_date = added_date + timedelta(days=row[5])
        days_left = (expiry_date - now).days
        if days_left <= 7:
            expiring.append((row[1], row[2], row[3], expiry_date.date(), days_left))
    return expiring
