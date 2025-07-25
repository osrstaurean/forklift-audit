#!/usr/bin/env python3
import sqlite3

DB_FILE = "forklift_audit.db"

def migrate():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    # 1) Ensure the audits table at least exists (with id & date)
    c.execute('''
    CREATE TABLE IF NOT EXISTS audits (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT
    )
    ''')

    # 2) Fetch existing column names
    c.execute("PRAGMA table_info(audits)")
    existing_cols = { row[1] for row in c.fetchall() }

    # 3) Define the full desired schema
    desired_cols = {
        'operator':             'TEXT',
        'forklift_id':          'TEXT',
        'tires':                'INTEGER',
        'brakes':               'INTEGER',
        'lights':               'INTEGER',
        'horn':                 'INTEGER',
        'forks':                'INTEGER',
        'fluid':                'INTEGER',
        'seatbelt':             'INTEGER',
        'comments':             'TEXT',
        'submitted_at':         'TEXT'
    }

    # 4) Add any columns that are missing
    for col_name, col_type in desired_cols.items():
        if col_name not in existing_cols:
            print(f"Adding column {col_name} {col_type}...")
            c.execute(f"ALTER TABLE audits ADD COLUMN {col_name} {col_type}")

    conn.commit()
    conn.close()
    print("Migration complete. Current columns:")
    # Re‑print final schema
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("PRAGMA table_info(audits)")
    for cid, name, ctype, notnull, dflt, pk in c.fetchall():
        print(f" - {name} ({ctype})")
    conn.close()

if __name__ == "__main__":
    migrate()
