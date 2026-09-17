import sqlite3
import os

DB_FILE = "rizzis_platform.db"


def get_connection():
    """Establishes a safe connection to the local SQLite file database."""
    return sqlite3.connect(DB_FILE, check_same_thread=False)


def initialize_database():
    """Creates the structural tables for your tracking system if they don't exist yet."""
    conn = get_connection()
    cursor = conn.cursor()

    # 1. Core Task Management Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            due_date TEXT NOT NULL,
            priority TEXT NOT NULL,
            create_date TEXT NOT NULL,
            category TEXT NOT NULL,
            status TEXT DEFAULT 'Active',
            notes TEXT DEFAULT ''
        )
    """)

    # 2. AUX Stopwatch Runtime Log Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS aux_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            log_date TEXT NOT NULL,
            aux_unit TEXT NOT NULL,
            duration_seconds INTEGER DEFAULT 0
        )
    """)

    conn.commit()
    conn.close()


# Automatically run the initializer configuration when imported
if not os.path.exists(DB_FILE):
    initialize_database()
